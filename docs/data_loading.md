# Usage

## Input data format

SARXarray works with coregistered SLC/interferogram stack. SARXarray provides a reader to perform lazy loading on data stacks in different file formats, including binary format. However, we recommend to store the coregistered stack in [`zarr`](https://zarr.readthedocs.io/en/stable/) format, and directly load them as an Xarray object by [`xarray.open_zarr`](https://docs.xarray.dev/en/stable/generated/xarray.open_zarr.html). 


## Loading coregistered SLC stack in binary format

If the stack is saved in binary format, it can be read by `SARXarray` under two pre-requisites:

1. All SLCs/interferograms have the same known raster size and data type;
2. All SLCs/interferograms have been resampled to the same raster grid.

For example, let's consider a case of a stack with three SLCs:

```python
import numpy as np
list_slcs = ['data/slc_1.raw', 'data/slc_2.raw', 'data/slc_3.raw']
shape = (10018, 68656) # (azimuth, range)
dtype = np.complex64
```

We built a list `list_slcs` with the paths to the SLCs. In this case they are stored in the same directory called `data`. The shape of each SLC should be provided, i.e.: `10018` pixels in `azimuth` direction, and `68656` in range direction. The data type is `numpy.complex64`.

The coregistered SLC stack can be read using the `from_binary` function:

```python
import sarxarray

stack = sarxarray.from_binary(list_slcs, shape, dtype=dtype)
```
You can also skip the `dtype` argument since it's defaulted to `numpy.complex64`. The stack will be read as an `xarray.Dataset` object, with data variables lazily loaded as `Dask Array`:

```python
print(stack)
```

```output
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

## Reading metadata

SARXarray provides a function to read metadata from the interferogram stack corregistered by Doris v4 or Doris v5. The metadata is read as a dictionary from the `slave.res` file under the folder of each SLC.

### Doris v4 metadata

A common Doris v4 output folder structure is as follows:

```
stack/
├── YYYYMMDD1/
│   ├── slc_1.res
│   ├── slc_1.raw
│   ├── ...
├── YYYYMMDD2/
│   ├── slc_2.res
│   ├── slc_2.raw
│   ├── ...
...
```

Where `YYYYMMDD1`, `YYYYMMDD2`, etc. are the acquisition dates of the SLCs, and `slc_1.res`, `slc_2.res`, etc. are the metadata files for each SLC.

To read the metadata from the Doris v4 stack, first build a list of the SLC metadata files:

```python
from pathlib import Path
stack_folder = Path('stack/')
res_file_list = list(tsx_folder.glob('???????/slave.res'))
```

where the pattern `???????` matches the date folders. Then, you can use the `read_metadata` function with the `driver` argument set to `"doris4"`:

```python
import sarxarray
metadata = sarxarray.read_metadata(res_file_list, driver="doris4")
```

### Doris v5 metadata
A common Doris v5 output folder structure is as follows:

```text
├── YYYYMMDD1/
│   ├── slc_1.res
│   ├── ifgs_1.res
│   ├── slc_1.raw
│   ├── ...
├── YYYYMMDD2/
│   ├── slc_2.res
│   ├── ifgs_2.res
│   ├── slc_2.raw
│   ├── ...
...
```

Where `YYYYMMDD1`, `YYYYMMDD2`, etc. are the acquisition dates of the SLCs, and `slc_1.res`, `slc_2.res`, etc. are the metadata files for each SLC. The files `ifgs_1.res`, `ifgs_2.res`, etc. are the metadata files for each interferogram, which contain the information of the sizes of the corregistered interferograms.

To read the metadata from the Doris v5 stack, first build a list of the SLC metadata files:

```python
from pathlib import Path
stack_folder = Path('stack/')
res_file_list = list(stack_folder.glob('???????/slc_*.res'))
```

Then, you can use the `read_metadata` function with the `driver` argument set to `"doris5"`:

```python
import sarxarray
metadata = sarxarray.read_metadata(res_file_list, driver="doris5")
```

`read_metadata` assumes that `ifgs_*.res` files are in the same folder as the `slc_*.res` files, and will read the interferogram sizes from them.