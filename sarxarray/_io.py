import dask
import numpy as np
import xarray as xr
import dask.array as da
import sarxarray.stack

from .conf import _dtypes

# Example: https://docs.dask.org/en/stable/array-creation.html#memory-mapping
def from_binary(slc_files, shape, vlabel="complex", dtype=np.float32, blocksize=5):
    """
    Read a SLC stack or relabted variables from binary files

    Parameters
    ----------
    slc_files : Iterable
        Paths to the SLC files. 
    shape : Tuple
        Shape of each SLC file, in (n_azimuth, n_range)
    vlabel : str, optional
        Name of the variable to read, by default "complex".
    dtype : numpy.dtype, optional
        Data type of the file to read, by default np.float32
    blocksize : int, optional
        chunk size, by default 5

    Returns
    -------
    xarray.Dataset
        returns an xarray.Dataset with three dimensions: (azimuth, range, time).

    """

    # Check dtype
    if not np.dtype(dtype).isbuiltin:
        if not all([name in (("re", "im")) for name in dtype.names]):
            raise TypeError(
                ('The customed dtype should have only two field names: '
                '"re" and "im". For example: '
                'dtype = np.dtype([("re", np.float32), ("im", np.float32)]).')
            )

    # Initialize stack as a Dataset
    coords = {
        "azimuth": range(shape[0]),
        "range": range(shape[1]),
        "time": range(len(slc_files)),
    }
    stack = xr.Dataset(coords=coords)

    # Read in all SLCs
    slcs = None
    for f_slc in slc_files:
        if slcs is None:
            slcs = read_slc(f_slc, shape, dtype, blocksize).reshape(
                (shape[0], shape[1], 1)
            )
        else:
            slc = read_slc(f_slc, shape, dtype, blocksize).reshape(
                (shape[0], shape[1], 1)
            )
            slcs = da.concatenate([slcs, slc], axis=2)
    

    # unpack the customized dtype
    if not np.dtype(dtype).isbuiltin:
        meta_arr = np.array((), dtype=_dtypes['complex'])
        slcs = da.apply_gufunc(
            _unpack_complex, "()->()", slcs, meta=meta_arr
        )
    
    stack = stack.assign({vlabel: (("azimuth", "range", "time"), slcs)})

    # If reading complex data, automatically
    if vlabel == "complex":
        stack = stack.slcstack._get_amplitude()
        stack = stack.slcstack._get_phase()

    return stack


def read_slc(filename_or_obj, shape, dtype, blocksize):

    slc = _mmap_dask_array(
        filename=filename_or_obj, shape=shape, dtype=dtype, blocksize=blocksize
    )

    return slc


def _mmap_dask_array(filename, shape, dtype, blocksize):
    """
    Create a Dask array from raw binary data in :code:`filename`
    by memory mapping.

    This method is particularly effective if the file is already
    in the file system cache and if arbitrary smaller subsets are
    to be extracted from the Dask array without optimizing its
    chunking scheme.

    It may perform poorly on Windows if the file is not in the file
    system cache. On Linux it performs well under most circumstances.

    Parameters
    ----------

    filename : str
    shape : tuple
        Total shape of the data in the file
    dtype:
        NumPy dtype of the data in the file
    blocksize : int, optional
        Chunk size for the outermost axis. The other axes remain unchunked.

    Returns
    -------

    dask.array.Array
        Dask array matching :code:`shape` and :code:`dtype`, backed by
        memory-mapped chunks.
    """
    load = dask.delayed(_mmap_load_chunk)
    chunks = []
    for index in range(0, shape[0], blocksize):
        # Truncate the last chunk if necessary
        chunk_size = min(blocksize, shape[0] - index)
        chunk = dask.array.from_delayed(
            load(
                filename,
                shape=shape,
                dtype=dtype,
                sl=slice(index, index + chunk_size),
            ),
            shape=(chunk_size,) + shape[1:],
            dtype=dtype,
        )
        chunks.append(chunk)
    return da.concatenate(chunks, axis=0)


def _mmap_load_chunk(filename, shape, dtype, sl):
    """
    Memory map the given file with overall shape and dtype and return a slice
    specified by :code:`sl`.

    Parameters
    ----------

    filename : str
    shape : tuple
        Total shape of the data in the file
    dtype:
        NumPy dtype of the data in the file
    sl:
        Object that can be used for indexing or slicing a NumPy array to
        extract a chunk

    Returns
    -------

    numpy.memmap or numpy.ndarray
        View into memory map created by indexing with :code:`sl`,
        or NumPy ndarray in case no view can be created using :code:`sl`.
    """
    data = np.memmap(filename, mode="r", shape=shape, dtype=dtype)
    return data[sl]


def _unpack_complex(complex):
    return complex['re'] + 1j*complex['im']
