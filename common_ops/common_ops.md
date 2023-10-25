# Common SLC operations

Common SAR processings can be performed by SARXarray. Below are some examples:

## Multi-look

Multi-look by a windowsize, e.g. 2 in azimuth dimension and 4 in range dimension:

```python
stack_multilook = stack.slcstack.multi_look((2,4))
```

## Coherence
Compute coherence between two SLCs:

```python
slc1 = stack.isel(time=[0]) # first image
slc2 = stack.isel(time=[2]) # third image
window = (4,4)

coherence = slc1.slcstack.complex_coherence(slc2, window)
```

## Mean-Reflection-Map (MRM)
```python
mrm = stack_multilook.slcstack.mrm()
```

```python
from matplotlib import pyplot as plt
fig, ax = plt.subplots()
ax.imshow(mrm)
mrm.plot(ax=ax, robust=True, cmap='gray')
```

## Point selection
A selection based on temporal properties per pixel can be performed. For example, we can select the Persistent Scatters (PS) by temporal dispersion of `amplitude`:

```python
ps = stack.slcstack.point_selection(threshold=0.25, method="amplitude_dispersion")
```