import dask.array as da
import numpy as np
import xarray as xr

from .conf import _dtypes
from .utils import multi_look


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
        """Compute a Mean Reflection Map (MRM)."""
        t_order = list(self._obj.dims.keys()).index("time")  # Time dimension order
        return self._obj.amplitude.mean(axis=t_order)

    def point_selection(self, threshold, method="amplitude_dispersion", chunks=1000):
        """Select pixels from a Stack, and return a Space-Time Matrix.

        The selection method is defined by `method` and `threshold`.
        The selected pixels will be reshaped to (space, time), where `space` is
        the number of selected pixels. The unselected pixels will be discarded.
        The original `azimuth` and `range` coordinates will be persisted.

        Parameters
        ----------
        threshold : float
            Threshold value for selection
        method : str, optional
            Method of selection, by default "amplitude_dispersion"
        chunks : int, optional
            Chunk size in the space dimension, by default 1000

        Returns
        -------
        xarray.Dataset
            An xarray.Dataset with two dimensions: (space, time).
        """
        match method:
            case "amplitude_dispersion":
                mask = self._amp_disp() < threshold
            case _:
                raise NotImplementedError

        # Get the 1D index on space dimension
        mask_1d = mask.stack(space=("azimuth", "range")).drop_vars(
            ["azimuth", "range", "space"]
        )
        index = mask_1d.space.data[mask_1d.data]  # Evaluate the mask

        # Reshape from Stack ("azimuth", "range", "time") to Space-Time Matrix
        # ("space", "time")
        stacked = self._obj.stack(space=("azimuth", "range"))
        stm = stacked.drop_vars(
            ["space", "azimuth", "range"]
        )  # this will also drop azimuth and range
        stm = stm.assign_coords(
            {
                "azimuth": (["space"], stacked.azimuth.data),
                "range": (["space"], stacked.range.data),
            }
        )  # keep azimuth and range index

        # Apply selection
        stm_masked = stm.sel(space=index)

        # Re-order the dimensions to
        # community preferred ("space", "time") order
        # Since there are dask arrays in stm_masked,
        # this operation is lazy.
        # Therefore its effect can be observed after evaluation
        stm_masked = stm_masked.transpose("space", "time")

        # Rechunk is needed because after apply maksing,
        # the chunksize will be in consistant
        stm_masked = stm_masked.chunk(
            {
                "space": chunks,
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

    def multi_look(
        self, window_size, method="coarsen", statistics="mean", compute=True
    ):
        """Perform multi-looking on a Stack, and return a Stack.

        Parameters
        ----------
        data : xarray.Dataset
            The data to be multi-looked.
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
            An `xarray.Dataset` with coarsen shape if
            `compute` is True, otherwise a `dask.delayed.Delayed` object.
        """
        return multi_look(self._obj, window_size, method, statistics, compute)


def _compute_amp(complex):
    return np.abs(complex)


def _compute_phase(complex):
    return np.angle(complex)
