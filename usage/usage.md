# Usage

## Input data format

SARXarry works with corregitserred SLC / interferogram stack. Conventionally they are provided in binary format. SARXarry provides a reader to perform lazy loading on a binary stack. However, we recommend to store the corregitserred stack in [`zarr`](https://zarr.readthedocs.io/en/stable/) format, and directly load them as an Xarray object by [`xarray.open_zarr`](https://docs.xarray.dev/en/stable/generated/xarray.open_zarr.html). 


## Loading corregisterred SLC stack in binary format

If the stack is saved in binary fomat, it can be read by `SARXarray` under two prerequisites:

1. All SLCs/interferograms have the same known raster size and data type;
2. All SLCs/interferograms have been resampled to the same raster grid.

For example, let's consider a case of an stack with three SLCs:

```python
import numpy as np
list_slcs = ['data/slc_1.raw', 'data/slc_2.raw', 'data/slc_3.raw']
shape = (10018, 68656) # (azimuth, range)
dtype = np.complex64
```

We built a list `list_slcs` with the paths to the SLCs. In this case they are stored in the same directory called `data`. The shape of each SLC is known: `10018` pixels in `azimuth` direction, and `68656` in range direction. The data type is `numpy.complex64`.

The corregisterred SLC stack can be read using `from_binary` function:

```python
import sarxarray

stack = sarxarray.from_binary(list_slcs, shape, dtype=dtype)
```
You can also skip the `dtype` argument since it's defaulted to `np.complex64`. The stack will be read as an `xarray.Dataset` object, with data variables lazily loaded as `Dask Array`:

```output
print(stack)

<xarray.Dataset>
Dimensions:    (azimuth: 10018, range: 68656, time: 3)
Coordinates:
  * azimuth    (azimuth) int64 0 1 2 3 4 5 ... 10013 10014 10015 10016 10017
  * range      (range) int64 0 1 2 3 4 5 ... 68650 68651 68652 68653 68654 68655
  * time       (time) int64 0 1 2
Data variables:
    complex    (azimuth, range, time) complex64 dask.array<chunksize=(4000, 4000, 1), meta=np.ndarray>
    amplitude  (azimuth, range, time) float32 dask.array<chunksize=(4000, 4000, 1), meta=np.ndarray>
    phase      (azimuth, range, time) float32 dask.array<chunksize=(4000, 4000, 1), meta=np.ndarray>
```

The loading chunk size can also be specified manually:

```python
stack_smallchunk = sarxarray.from_binary(list_slcs, shape, chunks=(2000, 2000))
```

## Common processing on an SLC stack

Common SAR processings can be performed by SARXarray. Below are some examples:

### Multi-look

Multi-look by a windowsize, e.g. 2 in azimuth dimension and 4 in range dimension:

```python
stack_multilook = stack.slcstack.multi_look((2,4))
```

### Coherence
Compute coherence between two SLCs:

```python
slc1 = stack.isel(time=[0]) # first image
slc2 = stack.isel(time=[2]) # third image
window = (4,4)

coherence = slc1.slcstack.complex_coherence(slc2, window)
```

### Mean-Reflection-Map (MRM)
```python
mrm = stack_multilook.slcstack.mrm()
```

```python
from matplotlib import pyplot as plt
fig, ax = plt.subplots()
ax.imshow(mrm)
mrm.plot(ax=ax, robust=True, cmap='gray')
```

### Point selection
A selection based on temporal properties per pixel can be performed. For example, we can select the Persistent Scatters (PS) by temporal dispersion of `amplitude`:

```python
ps = stack.slcstack.point_selection(threshold=0.25, method="amplitude_dispersion")
```

## Manipulate an SLC stack as an Xarray

The loaded stack can be manipulated as an `Xarray.Dataset` instance.

Slice the SLC stack in 3D:

```python
stack.isel(azimuth=range(1000,2000), range=range(1500,2500), time=range(2,5))
```

Select `amplitude` attributes
```python
amp = stack['amplitude']
```

Compute stack and peresist in memory:
```python
stack = stack.compute()
```








