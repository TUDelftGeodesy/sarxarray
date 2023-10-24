import copy
import numpy as np
import xarray as xr
import dask.array as da
import dask.delayed as delayed
import warnings

from .conf import _dtypes


@xr.register_dataset_accessor("slcstack")
class Stack:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def _get_amplitude(self):
        meta_arr = np.array((), dtype=_dtypes["float"])
        amplitude = da.apply_gufunc(
            _compute_amp, "()->()", self._obj.complex, meta=meta_arr
        )
        self._obj = self._obj.assign(
            {"amplitude": (("azimuth", "range", "time"), amplitude)}
        )
        return self._obj

    def _get_phase(self):
        meta_arr = np.array((), dtype=_dtypes["float"])
        phase = da.apply_gufunc(
            _compute_phase, "()->()", self._obj.complex, meta=meta_arr
        )
        self._obj = self._obj.assign({"phase": (("azimuth", "range", "time"), phase)})
        return self._obj

    def mrm(self):
        t_order = list(self._obj.dims.keys()).index("time")  # Time dimension order
        return self._obj.amplitude.mean(axis=t_order)

    def point_selection(self, threshold, method="amplitude_dispersion", chunks=1000):
        """
        Select pixels from a Stack, and return a Space-Time Matrix.

        The selection method is defined by `method` and `threshold`. The selected pixels will be reshaped to (points, time), where `points` is the number of selected pixels. The unselected pixels will be discarded. The original `azimuth` and `range` coordinates will be persisted.

        Parameters
        ----------
        threshold : float
            Threshold value for selection
        method : str, optional
            Method of selection, by default "amplitude_dispersion"
        chunks : int, optional
            Chunk size in the points dimension, by default 1000

        Returns
        -------
        xarray.Dataset
            An xarray.Dataset with two dimensions: (points, time).
        """

        match method:
            case "amplitude_dispersion":
                mask = self._amp_disp() < threshold
            case other:
                raise NotImplementedError

        # Get the 1D index on points dimension
        mask_1d = mask.stack(points=("azimuth", "range")).drop_vars(
            ["azimuth", "range", "points"]
        )
        index = mask_1d.points.data[mask_1d.data]  # Evaluate the mask

        # Reshape from Stack ("azimuth", "range", "time") to Space-Time Matrix ("points", "time")
        stacked = self._obj.stack(points=("azimuth", "range"))
        stm = stacked.drop_vars(["points"])  # this will also drop azimuth and range
        stm = stm.assign_coords(
            {
                "azimuth": (["points"], stacked.azimuth.data),
                "range": (["points"], stacked.range.data),
            }
        )  # keep azimuth and range index

        # Apply selection
        stm_masked = stm.sel(points=index)

        # Re-order the dimensions to community preferred ("points", "time") order
        # Since there are dask arrays in stm_masked, this operation is lazy. Therefore its effect can be observed after evaluation
        stm_masked = stm_masked.transpose("points", "time")

        # Rechunk
        # Rechunk is needed because after apply maksing, the chunksize will be in consistant
        stm_masked = stm_masked.chunk(
            {
                "points": chunks,
                "time": -1,
            }
        )

        return stm_masked

    def _amp_disp(self, chunk_azimuth=500, chunk_range=500):
        # Time dimension order
        t_order = list(self._obj.dims.keys()).index("time")

        # Rechunk to make temporal operation more efficient
        amplitude = self._obj.amplitude.chunk(
            {"azimuth": chunk_azimuth, "range": chunk_range, "time": -1}
        )

        amplitude_dispersion = amplitude.std(axis=t_order) / (
            amplitude.mean(axis=t_order) + np.finfo(amplitude.dtype).eps
        )  # adding epsilon to avoid zero division

        return amplitude_dispersion

    def multi_look(self, window_size, method="coarsen", statistics="mean", compute=True):
        """
        Perform multi-looking on a Stack, and return a Stack.

        Parameters
        ----------
        window_size : tuple
            Window size for multi-looking, in the format of (azimuth, range)
        method : str, optional
            Method of multi-looking, by default "coarsen"
        statistics : str, optional
            Statistics method for multi-looking, by default "mean"
        compute : bool, optional
            Whether to compute the result, by default True. If False, the result
            will be `dask.delayed.Delayed`. This is useful when the multi_look
            is used as an intermediate result.

        Returns
        -------
        xarray.Dataset
            An `xarray.Dataset` with coarsen shape if `compute` is True,
            otherwise a `dask.delayed.Delayed` object.
        """
        # set the chunk size
        if not self._obj.chunks:
            self._obj = self._obj.chunk(
            {
                "azimuth": "auto",
                "range": "auto",
                "time": -1,
            })
        chunk = (self._obj.chunks["azimuth"][0], self._obj.chunks["range"][0])

        # check if window_size is valid
        if window_size[0] > self._obj.azimuth.size or window_size[1] > self._obj.range.size:
            warnings.warn(
                "Window size is larger than the data size, no multi-looking is performed."
            )
            return self._obj

        # check if window_size is smaller than chunk size
        if window_size[0] > chunk[0] or window_size[1] > chunk[1]:
            warnings.warn(
                "Window size is larger than chunk size, no multi-looking is performed."
            )
            return self._obj

        # add new atrrs here because Delayed objects are immutable
        self._obj.attrs["multi-look"] = f"{method}-{statistics}"

        # define custom coordinate function to define new coordinates starting
        # from 0: the inputs `reshaped` and `axis` are output of
        # `coarsen_reshape` internal function and are passed to the `coord_func`
        def _custom_coord_func(reshaped, axis):
            if axis[0] == 1 or 2:
                return np.arange(0, reshaped.shape[0], 1, dtype=int)
            else:
                return reshaped.flatten()

        match method:
            case "coarsen":
                # TODO: if boundary and size should be configurable
                multi_looked = self._obj.coarsen(
                    {"azimuth": window_size[0], "range": window_size[1]},
                    boundary="trim",
                    side="left",
                    coord_func=_custom_coord_func,
                )
            case other:
                raise NotImplementedError

        # apply statistics
        stat_functions = {
            "mean": multi_looked.mean,
            "median": multi_looked.median,
        }
        if statistics in stat_functions:
            stat_function = stat_functions[statistics]
            if compute:
                multi_looked = stat_function(keep_attrs=True)
            else:
                multi_looked = delayed(stat_function)(keep_attrs=True)
        else:
            NotImplementedError

        # Rechunk is needed because shape of the data will be changed after
        # multi-looking
        # calculate new chunck size based on the window size and the existing
        # chunk size
        chunk = (int(np.ceil(chunk[0] / window_size[0])),
                 int(np.ceil(chunk[1] / window_size[1])))

        multi_looked = multi_looked.chunk(
            {
                "azimuth": chunk[0],
                "range": chunk[1],
                "time": -1,
            }
        )

        return multi_looked

    def complex_coherence(self, other, window_size, compute=True):
        """
        Calculate complex coherence of two images.
        # TODO: add a reference
        assume two images reference (R), here `self` and other (O), the coherence is defined as:
        numerator = mean(R * O`) in the window
        denominator = mean(R * R`) * mean(O * O`) in the window
        coherence = abs( numerator / sqrt(denominator) )

        Parameters
        ----------
        other : xarray.Dataset
            The other image to calculate complex coherence with.
        window_size : tuple
            Window size for multi-looking, in the format of (azimuth, range)
        compute : bool, optional
            Whether to compute the result, by default True. If False, the result
            will be `dask.delayed.Delayed`. This is useful when the complex_coherence
            is used as an intermediate result.

        Returns
        -------
        xarray.Dataset
            An `xarray.Dataset` if `compute` is True,
            otherwise a `dask.delayed.Delayed` object.
        """
        # check if the two images have the same shape
        if self._obj.azimuth.size != other.azimuth.size or self._obj.range.size != other.range.size:
            raise ValueError("The two images have different shape.")

        # copy the original data to a new object to avoid changing the original
        # data
        new = self._obj.copy(deep=False)

        # calculate the numerator of the equation
        self._obj = new * other.conj()
        numerator = self.multi_look(window_size, method="coarsen", statistics="mean", compute=compute)

        # calculate the denominator of the equation
        self._obj = new * new.conj()
        self_mean = self.multi_look(window_size, method="coarsen", statistics="mean", compute=compute)

        self._obj = other * other.conj()
        other_mean = self.multi_look(window_size, method="coarsen", statistics="mean", compute=compute)

        denominator = self_mean * other_mean

        # calculate the coherence
        def _compute_coherence(numerator, denominator):
            return np.abs(numerator / np.sqrt(denominator))

        if compute:
            coherence = _compute_coherence(numerator, denominator)
        else:
            coherence = delayed(_compute_coherence)(numerator, denominator)

        return coherence


def _compute_amp(complex):
    return np.abs(complex)


def _compute_phase(complex):
    return np.angle(complex)
