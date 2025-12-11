import logging
import math
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal

import dask
import dask.array as da
import numpy as np
import xarray as xr

from .conf import (
    META_ARRAY_KEYS,
    META_FLOAT_KEYS,
    META_INT_KEYS,
    META_UNIT_CONVERSION_MULTIPLICATION_KEYS_DORIS4,
    META_UNIT_CONVERSION_MULTIPLICATION_KEYS_DORIS5,
    RE_PATTERNS_DORIS4,
    RE_PATTERNS_DORIS5,
    RE_PATTERNS_DORIS5_IFG,
    TIME_FORMAT_DORIS4,
    TIME_FORMAT_DORIS5,
    TIME_STAMP_KEY,
    _dtypes,
    _memsize_chunk_mb,
)

logger = logging.getLogger(__name__)


def from_dataset(ds: xr.Dataset) -> xr.Dataset:
    """Create a SLC stack or from an Xarray Dataset.

    This function create tasks graph converting the two data variables of complex data:
    `real` and `imag`, to three variables: `complex`, `amplitude`, and `phase`.

    The function is intented for an SLC stack in `xr.Dataset` loaded from a Zarr file.

    For other datasets, such as lat, lon, etc., please use `xr.open_zarr` directly.

    Parameters
    ----------
    ds : xr.Dataset
        SLC stack loaded from a Zarr file.
        Must have three dimensions: `(azimuth, range, time)`.
        Must have two variables: `real` and `imag`.

    Returns
    -------
    xr.Dataset
        Converted SLC stack.
        An xarray.Dataset with three dimensions: `(azimuth, range, time)`, and
        three variables: `complex`, `amplitude`, `phase`.

    Raises
    ------
    ValueError
        The input dataset should have three dimensions: `(azimuth, range, time)`.
    ValueError
        The input dataset should have the following variables: `('real', 'imag')`.
    """
    # Check ds should have the following dimensions: (azimuth, range, time)
    if any(dim not in ds.sizes for dim in ["azimuth", "range", "time"]):
        raise ValueError(
            "The input dataset should have three dimensions: (azimuth, range, time)."
        )

    # Check ds should have the following variables: ("real", "imag")
    if any(var not in ds.variables for var in ["real", "imag"]):
        raise ValueError(
            "The input dataset should have the following variables: ('real', 'imag')."
        )

    # Construct the three datavariables: complex, amplitude, and phase
    ds["complex"] = ds["real"] + 1j * ds["imag"]
    ds = ds.slcstack._get_amplitude()
    ds = ds.slcstack._get_phase()

    # Remove the original real and imag variables
    ds = ds.drop_vars(["real", "imag"])

    return ds


def from_binary(
    slc_files, shape, vlabel="complex", dtype=np.complex64, chunks=None, ratio=1
):
    """Read a SLC stack or related variables from binary files.

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


def read_metadata(
    files: str | list | Path,
    driver: Literal["doris4", "doris5"] = "doris5",
    ifg_file_name: str = "ifgs.res",
) -> dict:
    """Read metadata of a coregistered interferogram stack.

    This function reads metadata from one or more metadata files from a coregistered
    interferogram stack, and returns the metadata as a dictionary format.

    This function supports two drivers: "doris4" for DORIS4 metadata files, e.g.
    coregistration results from TerraSAR-X; "doris5" for DORIS5 metadata files,
    e.g. coregistration results from Sentinel-1. More support for other drivers
    will be added in the future.

    For drivers "doris4" and "doris5", it parses the metadata with predefined regular
    expressions, returning a dictionary with predefined keys. Check conf.py for
    available keys and regular expressions.

    Specifically for the "doris5" driver, it is assumed that there is a "ifgs.res" file
    next to the input metadata file, which contains the interferogram size information.
    If the "ifgs.res" file is not found, the interferogram size information will
    not be included in the metadata.

    If a single file is provided, it reads the metadata from that file.

    If multiple files are provided, the function will read the metadata from each file,
    and combine the results based on the following rules:
    - If a metadata key has values in string format or integer format, it combines the
    values into a set.
    - If a metadata key has values in float format, and the standard deviation is less
    than 1% of the mean, it takes the average of the values.
    - For the two Doris drivers "doris4" or "doris5", if the metadata key is
    TIME_STAMP_KEY, it treats it as the timestamp of acquisition and
    converts it to a numpy array of datetime64 format, sorted in ascending order.


    Parameters
    ----------
    files : str | list | Path
        Path(s) to the metadata files.
    driver : str, optional
        The driver to use for reading metadata. Supported drivers are "doris4" and
        "doris5". Default is "doris5".
    ifg_file_name : str, optional
        The name of the interferogram size file for the "doris5" driver.
        We assume this file is next to each metadata file and use it to read the
        interferogram size information. if it is not found, the size
        information will not be included in the metadata. Default is "ifgs.res".

    Returns
    -------
    dict
        Dictionary containing the metadata read from the files.

    Raises
    ------
    NotImplementedError
        If the driver is not "doris4" or "doris5".
    """
    # Check driver
    if driver not in ["doris4", "doris5"]:
        raise NotImplementedError(
            f"Driver '{driver}' is not implemented. "
            "Supported drivers are: 'doris4', 'doris5'."
        )

    # If there is only one file, convert it to a list
    if not isinstance(files, list):
        files = [files]

    # Force all files to be Path objects in case files is a list of strings
    files = [Path(file) for file in files]

    # Parse metadata from each file
    # if a key does not exists, a list will be created
    metadata = defaultdict(list)
    for file in files:
        res = _parse_metadata(file, driver, ifg_file_name)
        for key, value in res.items():
            metadata[key].append(value)

    # Regulate metadata for all files
    metadata = _regulate_metadata(metadata, driver)

    return metadata


def _parse_metadata(file, driver, ifg_file_name):
    """Parse a single metadata file to a dictionary of strings."""
    # Select the appropriate patterns based on the driver
    if driver == "doris5":
        patterns = RE_PATTERNS_DORIS5
        patterns_ifg = RE_PATTERNS_DORIS5_IFG
    elif driver == "doris4":
        patterns = RE_PATTERNS_DORIS4
        patterns_ifg = None
    else:
        raise NotImplementedError(
            f"Driver '{driver}' is not implemented. "
            "Supported drivers are: 'doris4', 'doris5'."
        )

    # Open the file
    with open(file) as f:
        content = f.read()

    # Read common metadata patterns
    results = {}
    for key, pattern in patterns.items():
        if key in META_ARRAY_KEYS.keys():  # multiple hits allowed
            matches = re.findall(pattern, content)
            if matches:
                results[key] = matches
            else:
                results[key] = None
        else:
            match = re.search(pattern, content)
            if match:
                results[key] = match.group(1)
            else:
                results[key] = None

    # Doris5 has size information in ifgs.res file
    # Try to get the ifg size from ifgs.res next to slave.res, if it exists
    if patterns_ifg is not None:
        file_ifg = file.with_name(ifg_file_name)
        if file_ifg.exists():
            with open(file_ifg) as f_ifg:
                content_ifg = f_ifg.read()
                for key, pattern in RE_PATTERNS_DORIS5_IFG.items():
                    if key in META_ARRAY_KEYS.keys():  # multiple hits allowed
                        matches = re.findall(pattern, content_ifg)
                        if matches:
                            results[key] = matches
                        else:
                            results[key] = None
                    else:
                        match = re.search(pattern, content_ifg)
                        if match:
                            results[key] = match.group(1)
                        else:
                            results[key] = None

    return results


def _regulate_metadata(metadata, driver):
    """Regulate metadata strings.

    This function processes the metadata read from the DORIS files, which are strings,
    and converts according to the types specified in META_FLOAT_KEYS and META_INT_KEYS.

    Check the documentation of `read_metadata` for the rules applied to the metadata.
    """
    # Convert time metadata from string to datetime
    if driver == "doris5":
        time_format = TIME_FORMAT_DORIS5
        unit_conversions = META_UNIT_CONVERSION_MULTIPLICATION_KEYS_DORIS5
    elif driver == "doris4":
        time_format = TIME_FORMAT_DORIS4
        unit_conversions = META_UNIT_CONVERSION_MULTIPLICATION_KEYS_DORIS4
    else:
        raise NotImplementedError(
            f"Driver '{driver}' is not implemented. "
            "Supported drivers are: 'doris4', 'doris5'."
        )

    list_time = []
    # If the time is a single string, convert it to a list
    if isinstance(metadata[TIME_STAMP_KEY], str):
        metadata[TIME_STAMP_KEY] = [metadata[TIME_STAMP_KEY]]
    for time in metadata[TIME_STAMP_KEY]:
        try:
            dt = datetime.strptime(time, time_format)
            list_time.append(np.datetime64(dt).astype("datetime64[s]"))
        except ValueError as e:
            raise ValueError(
                f"Invalid date format for key: '{TIME_STAMP_KEY}'. "
                f"Expected format is '{time_format}'."
            ) from e
    metadata[TIME_STAMP_KEY] = np.sort(np.array(list_time))

    for key, value in list(metadata.items()):
        # raise error if different types are found in value
        if len(set(type(v) for v in value)) > 1:
            raise TypeError(
                f"Inconsistency found in metadata key: {key}. "
                "Different types are found in the value list."
            )

        if key in META_ARRAY_KEYS.keys():  # need to regulate this one separately
            regulated_arrays = []
            for arr in metadata[key]:
                regulated_array = np.zeros((len(arr), len(arr[0])))
                for row in range(len(arr)):
                    for col in range(len(arr[row])):
                        regulated_array[row, col] = META_ARRAY_KEYS[key](arr[row][col])
                if key in unit_conversions.keys():
                    regulated_array *= unit_conversions[key]
                regulated_arrays.append(np.copy(regulated_array))

            metadata[key] = [
                np.copy(regulated_array) for regulated_array in regulated_arrays
            ]
            if len(metadata[key]) == 1:
                metadata[key] = metadata[key][0]

        else:
            # Only keep the unique values
            if isinstance(metadata[key], list):
                metadata[key] = set(value)

            # Unfold the single value set to strings
            if len(metadata[key]) == 1:
                metadata[key] = next(iter(metadata[key]))

            # if float, take the average unless std is larger than 1% of the mean
            if key in META_FLOAT_KEYS:
                # Convert to float
                arr = np.array(value, dtype=np.float64)
                if np.std(arr) / np.mean(arr) < 0.01:
                    metadata[key] = np.mean(arr).item()  # Convert to scalar
                else:
                    raise ValueError(
                        f"Inconsistency found in metadata key:  {key}. "
                        "Standard deviation is larger than 1% of the mean."
                    )
                if key in unit_conversions.keys():
                    metadata[key] *= unit_conversions[key]
            if key in META_INT_KEYS:
                if isinstance(metadata[key], str):
                    metadata[key] = int(metadata[key])
                    if key in unit_conversions.keys():
                        metadata[key] *= unit_conversions[key]
                elif len(metadata[key]) > 1:  # set with multiple values
                    if key in unit_conversions.keys():
                        metadata[key] = set(
                            [int(v) * unit_conversions[key] for v in metadata[key]]
                        )
                    else:
                        metadata[key] = set([int(v) for v in metadata[key]])
            if key in ["number_of_lines", "number_of_pixels"]:
                if isinstance(metadata[key], set):
                    warning_msg = f"Multiple values found in {key}: {metadata[key]}."
                    logger.warning(warning_msg)

    return metadata
