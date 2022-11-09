import os

import dask
import numpy as np
import xarray as xr
import dask.array as da


@xr.register_dataset_accessor("stack")
class Stack:
    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    
