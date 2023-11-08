import logging
import math

import dask
import dask.array as da
import numpy as np
import xarray as xr

from .conf import _dtypes, _memsize_chunk_mb

logger = logging.getLogger(__name__)

# Example: https://docs.dask.org/en/stable/array-creation.html#memory-mapping


def from_binary(
    slc_files, shape, vlabel="complex", dtype=np.complex64, chunks=None, ratio=1
):
    """Read a SLC stack or relabted variables from binary files.

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
    chunks : list, optional
        2-D chunk size, by default None
    ratio:
        Ratio of resolutions (azimuth/range), by default 1

    Returns
    -------
    xarray.Dataset
        An xarray.Dataset with three dimensions: (azimuth, range, time).

    """
    # Check dtype
    if not np.dtype(dtype).isbuiltin:
        if not all([name in (("re", "im")) for name in dtype.names]):
            raise TypeError(

                    "The customed dtype should have only two field names: "
                    '"re" and "im". For example: '
                    'dtype = np.dtype([("re", np.float32), ("im", np.float32)]).'

            )

    # Initialize stack as a Dataset
    coords = {
        "azimuth": range(shape[0]),
        "range": range(shape[1]),
        "time": range(len(slc_files)),
    }
    ds_stack = xr.Dataset(coords=coords)

    # Calculate appropriate chunk size if not user-defined
    if chunks is None:
        chunks = _calc_chunksize(shape, dtype, ratio)

    # Read in all SLCs
    slcs = None
    for f_slc in slc_files:
        if slcs is None:
            slcs = _mmap_dask_array(f_slc, shape, dtype, chunks).reshape(
                (shape[0], shape[1], 1)
            )
        else:
            slc = _mmap_dask_array(f_slc, shape, dtype, chunks).reshape(
                (shape[0], shape[1], 1)
            )
            slcs = da.concatenate([slcs, slc], axis=2)

    # unpack the customized dtype
    if not np.dtype(dtype).isbuiltin:
        meta_arr = np.array((), dtype=_dtypes["complex"])
        slcs = da.apply_gufunc(_unpack_complex, "()->()", slcs, meta=meta_arr)

    ds_stack = ds_stack.assign({vlabel: (("azimuth", "range", "time"), slcs)})

    # If reading complex data, automatically
    if vlabel == "complex":
        ds_stack = ds_stack.slcstack._get_amplitude()
        ds_stack = ds_stack.slcstack._get_phase()

    return ds_stack


def _mmap_dask_array(filename, shape, dtype, chunks):
    """Create a Dask array from raw binary data by memory mapping.

    This method is particularly effective if the file is already
    in the file system cache and if arbitrary smaller subsets are
    to be extracted from the Dask array without optimizing its
    chunking scheme.
    It may perform poorly on Windows if the file is not in the file
    system cache. On Linux it performs well under most circumstances.

    Parameters
    ----------
    filename : str
        The path to the file that contains raw binary data.
    shape : tuple
        Total shape of the data in the file
    dtype:
        NumPy dtype of the data in the file
    chunks : int, optional
        Chunk size for the outermost axis. The other axes remain unchunked.

    Returns
    -------
    dask.array.Array
        Dask array matching :code:`shape` and :code:`dtype`, backed by
        memory-mapped chunks.
    """
    load = dask.delayed(_mmap_load_chunk)
    range_chunks = []
    for azimuth_index in range(0, shape[0], chunks[0]):
        azimuth_chunks = []
        # Truncate the last chunk if necessary
        azimuth_chunk_size = min(chunks[0], shape[0] - azimuth_index)
        for range_index in range(0, shape[1], chunks[1]):
            # Truncate the last chunk if necessary
            range_chunk_size = min(chunks[1], shape[1] - range_index)
            chunk = dask.array.from_delayed(
                load(
                    filename,
                    shape=shape,
                    dtype=dtype,
                    sl1=slice(azimuth_index, azimuth_index + azimuth_chunk_size),
                    sl2=slice(range_index, range_index + range_chunk_size),
                ),
                shape=(azimuth_chunk_size, range_chunk_size),
                dtype=dtype,
            )
            azimuth_chunks.append(chunk)
        range_chunk = da.concatenate(azimuth_chunks, axis=1)
        range_chunks.append(range_chunk)
    return da.concatenate(range_chunks, axis=0)


def _mmap_load_chunk(filename, shape, dtype, sl1, sl2):
    """Memory map the given file with overall shape and dtype.

    It returns a slice specified by :code:`sl1` in azimuth direction and
    :code:`sl2` in range direction.

    Parameters
    ----------
    filename : str
        The path to the file that contains raw binary data.
    shape : tuple
        Total shape of the data in the file
    dtype:
        NumPy dtype of the data in the file
    sl1:
        Slice object in azimuth direction that can be used for indexing or
        slicing a NumPy array to extract a chunk
    sl2:
        Slice object in range direction that can be used for indexing or slicing
        a NumPy array to extract a chunk

    Returns
    -------
    numpy.memmap or numpy.ndarray
        View into memory map created by indexing with :code:`sl1` and
        :code:`sl2`, or NumPy ndarray in case no view can be created.
    """
    data = np.memmap(filename, mode="r", shape=shape, dtype=dtype)
    return data[sl1, sl2]


def _unpack_complex(complex):
    return complex["re"] + 1j * complex["im"]


def _calc_chunksize(shape: tuple, dtype: np.dtype, ratio: int):
    """Calculate an optimal chunking size.

    It calculates an optimal chunking size in the azimuth and range direction
    for reading with dask and store it in variable `chunks`.

    Parameters
    ----------
    shape : tuple
        Total shape of the data in the file
    dtype:
        NumPy dtype of the data in the file
    ratio:
        Ratio of resolutions (azimuth/range)

    Returns
    -------
    chunks: tuple
        Chunk sizes (as multiples of 1000) in the azimuth and range direction.
        Default value of [-1, -1] when unmodified activates this function.
    """
    n_elements = (
        _memsize_chunk_mb * 1024 * 1024 / np.dtype(dtype).itemsize
    )  # Optimal number of elements for a memory size of 100mb (first number)
    chunks_ra = (
        int(math.ceil((n_elements / ratio) ** 0.5 / 1000.0)) * 1000
    )  # Chunking size in range direction up to nearest thousand
    chunks_az = chunks_ra * ratio

    # Regulate chunk to the size of each dim
    chunks_az = min(chunks_az, shape[0])
    chunks_ra = min(chunks_ra, shape[1])

    chunks = (chunks_az, chunks_ra)

    return chunks
