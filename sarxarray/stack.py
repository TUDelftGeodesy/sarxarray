import numpy as np
import xarray as xr
import dask.array as da
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

    def point_selection(
        self, threshold, method="amplitude_dispersion", chunk_size=1000
    ):
        """
        Select pixels by thresholding, and return

        Parameters
        ----------
        threshold : float
            _description_
        method : str, optional
            Method of selection, by default "amplitude_dispersion"

        Returns
        -------
        xarray.Dataset
            An xarray.Dataset with two dimensions: (point, time).
        """
        match method:
            case "amplitude_dispersion":
                mask = self._amp_disp() > threshold
            case other:
                raise NotImplementedError

        # Apply mask
        # ToDo: make sure the mask has the same order of dimension, apart from time
        stack_masked = self._obj.where(mask)

        # Get space time matrix by stacking "azimuth" and "range" dimension to "points" dimension
        stm = stack_masked.stack(points=("azimuth", "range"))
        stm = stm.transpose("points", "time")  # reorder the dimensions

        # Evaluate the mask and rechunk
        # Rechunk is needed because after apply maksing, the chunksize will be in consistant
        # Temporally supress RuntimeWarning bacause of the zero division in std computation
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        stm_reshaped = stm.dropna(dim="points", how="all").chunk(
            {
                "points": chunk_size,
                "time": -1,
            }
        )
        warnings.filterwarnings("default", category=RuntimeWarning)

        # Replace the MultiIndex points coordinates with an ID to make it work with Zarr
        stm_reshaped = stm_reshaped.reset_index("points")
        stm_reshaped["points"] = xr.DataArray(
            data=range(stm_reshaped.points.size), dims=["points"]
        )
        return stm_reshaped

    def _amp_disp(self, chunk_azimuth=500, chunk_range=500):
        # Amplitude dispersion
        t_order = list(self._obj.dims.keys()).index("time")  # Time dimension order

        # Rechunk to make temporal operation more efficient
        amplitude = self._obj.amplitude.chunk(
            {"azimuth": chunk_azimuth, "range": chunk_range, "time": -1}
        )

        amplitude_dispersion = amplitude.mean(axis=t_order) / amplitude.std(
            axis=t_order
        )

        return amplitude_dispersion


def _compute_amp(complex):
    return np.abs(complex)


def _compute_phase(complex):
    return np.angle(complex)
