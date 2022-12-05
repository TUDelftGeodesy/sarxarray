import numpy as np
import xarray as xr
import dask.array as da

@xr.register_dataset_accessor("slcstack")
class Stack:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    @property
    def amplitude(self):
        empty_arr = np.array((), dtype=np.float32)
        return da.apply_gufunc(_compute_amp, "()->()", self._obj.complex, meta=empty_arr)
    
    def mrm(self):
        t_order = list(self._obj.dims.keys()).index('time') # Time dimmension order
        return self.amplitude.mean(axis=t_order)

def _compute_amp(complex):
    return np.sqrt(complex['re']**2 + complex['im']**2)



    
