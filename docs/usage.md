# Usage

```python
# List of path to binary SLC files
list_slcs = ['slc_1.raw', 'slc_2.raw', 'slc_3.raw']
```

```python
# Known 2D shape (azimuth, range)
shape = (10018, 68656)
```

## Loading corregisterred SLC stack
Read corregisterred SLC stack using `from_binary`:

```python
import sarxarray

stack = sarxarray.from_binary(list_slcs, shape) 
```

Manually specify chunk size:

```python
stack_smallchunk = sarxarray.from_binary(list_slcs, shape, chunks=(2000, 2000))
```

## Common processing on an SLC stack

Multi-look by a windowsize, e.g. 2 in azimuth dimension and 4 in range dimension.

```python
stack_multilook = stack.slcstack.multi_look((2,4))
```

Compute coherence between two SLCs:
```python
slc1 = stack.isel(time=[0]) # first image
slc2 = stack.isel(time=[2])  # third image
window = (4,4)

coherence = slc1.slcstack.complex_coherence(slc2, window)
```

## Make a Mean-Reflection-Map (MRM) and visualize

```python
# Get MRM
mrm = stack_multilook.slcstack.mrm()

# Visualize
from matplotlib import pyplot as plt
fig, ax = plt.subplots()
ax.imshow(mrm)
mrm.plot(ax=ax, robust=True, cmap='gray')
```

## Access and manipulate an SLC stack as an Xarray

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










