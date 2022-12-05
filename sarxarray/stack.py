import numpy as np
import xarray as xr
import dask.array as da

from .conf import _dtypes


@xr.register_dataset_accessor("slcstack")
class Stack:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def _get_amplitude(self):
        meta_arr = np.array((), dtype=_dtypes['float'])
        amplitude = da.apply_gufunc(
            _compute_amp, "()->()", self._obj.complex, meta=meta_arr
        )
        self._obj = self._obj.assign({"amplitude": (("azimuth", "range", "time"), amplitude)})
        return self._obj

    def _get_phase(self):
        meta_arr = np.array((), dtype=_dtypes['float'])
        phase = da.apply_gufunc(
            _compute_phase, "()->()", self._obj.complex, meta=meta_arr
        )
        self._obj = self._obj.assign({"phase": (("azimuth", "range", "time"), phase)})
        return self._obj

    def mrm(self):
        t_order = list(self._obj.dims.keys()).index("time")  # Time dimmension order
        return self._obj.amplitude.mean(axis=t_order)


def _compute_amp(complex):
    return np.abs(complex)


def _compute_phase(complex):
    return np.angle(complex)
