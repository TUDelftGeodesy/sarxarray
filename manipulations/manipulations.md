# Manipulate an SLC stack as an Xarray

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