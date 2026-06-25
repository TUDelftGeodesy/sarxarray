import json
import logging
import math
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

import dask
import dask.array as da
import numpy as np
import xarray as xr

from .conf import (
    META_ARRAY_KEYS,
    META_ARRAY_SHAPES_SNAP,
    META_FLOAT_KEYS,
    META_INT_KEYS,
    META_UNIT_CONVERSION_MULTIPLICATION_KEYS_DORIS4,
    META_UNIT_CONVERSION_MULTIPLICATION_KEYS_DORIS5,
    META_UNIT_CONVERSION_MULTIPLICATION_KEYS_SNAP,
    RE_PATTERNS_DORIS4,
    RE_PATTERNS_DORIS5,
    RE_PATTERNS_DORIS5_IFG,
    RE_PATTERNS_SNAP,
    TIME_FORMAT_DORIS4,
    TIME_FORMAT_DORIS5,
    TIME_FORMAT_SNAP,
    TIME_STAMP_KEY,
    _dtypes,
    _memsize_chunk_mb,
)

logger = logging.getLogger(__name__)


def from_dataset(ds: xr.Dataset) -> xr.Dataset:
    """Create a SLC stack or from an Xarray Dataset.

    This function create tasks graph converting the two data variables of complex data:
    `real` and `imag`, to three variables: `complex`, `amplitude`, and `phase`.

    The function is intended for an SLC stack in `xr.Dataset` loaded from a Zarr file.

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
    slc_files: list[str | Path],
    shape: tuple[int, int],
    vlabel: str = "complex",
    dtype: np.dtype = np.complex64,
    chunks: tuple[int, int] | None = None,
    ratio: float = 1,
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

    # Check if slc_files is a non empty Iterable and not a string
    if not hasattr(slc_files, "__iter__") or isinstance(slc_files, str):
        raise ValueError(
            "slc_files should be a non-empty Iterable and not a string."
            "If you have only one file, please put it in a list, e.g. slc_files=[file]."
        )
    if len(slc_files) == 0:
        raise ValueError("slc_files should be a non-empty Iterable.")

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


def from_snap_dataset(snap_znap_archives: list[str, Path]) -> xr.Dataset:
    """Read an SLC stack from a list of ZNAP archives produced by SNAP.

    SNAP produces .znap-archives, which are very similar to the .zarr
    archives used by sarxarray except for a few key differences:
    - ZNAPs use a local xy-coordinate system instead of radar coordinates
    - ZNAPs separate the real and complex part of the observation
    - SNAP produces one ZNAP for each image

    This function takes a series of ZNAPs and converts them to the
    standard sarxarray output: one .zarr archive with coordinates
    azimuth and range (corrected for the offset of the local coordinate
    system) and time, and the complex data layer for the observations.
    Additional data layers present in the ZNAP archives with xy-coordinates
    are passed on as well, either as (azimuth, range, time) variables (if
    present at a daughter epochs) or as (azimuth, range) variables (if
    present only at the mother epoch (which is automatically detected)).

    ZNAP archives can also contain 'tiepoint grids' with xt/yt coordinates.
    These layers are not passed on, as they do not fit into the azimuth/range
    coordinate system of sarxarray.

    Parameters
    ----------
    snap_znap_archives: list[str, Path]
        List of .znap archives to be read into an xarray Dataset

    Returns
    -------
    xr.Dataset
        Dataset containing:
            - the coordinates azimuth/range (corrected for cropping offsets) and time
            - complex data layer based on ZNAPs i and q data layers
            - amplitude and phase data layers as calculated from the complex data
            - any extra data layers present in the ZNAPs at a daughter acquisition as
                (azimuth, range, time) data variables
            - any extra data layers present only in the mother ZNAP archive as
                (azimuth, range) data variables

    Raises
    ------
    ValueError
        If `snap_znap_archives` is empty or not iterable
    """
    # Check if snap_znap_archives is a non empty Iterable and not a string
    if not hasattr(snap_znap_archives, "__iter__") or isinstance(
            snap_znap_archives, str
    ):
        raise ValueError(
            "snap_znap_archives should be a non-empty Iterable and not a string."
            "If you have only one file, please put it in a list, e.g. "
            "snap_znap_archives=[file]."
        )
    if len(snap_znap_archives) == 0:
        raise ValueError("snap_znap_archives should be a non-empty Iterable.")

    # in the .znaps, the dimension x is range, y is azimuth
    # xt and yt are interpolated values at coarse resolution
    full_data = {}
    mother_epoch = None

    for file in snap_znap_archives:
        data = xr.open_zarr(file, consolidated=False)
        data_layers = data.original_raster_data_node_order
        cur_epoch = data_layers[0].split("_")[-1]
        epoch = datetime.strptime(cur_epoch, "%d%b%Y").strftime("%Y%m%d")

        # there are two types of layers: full data layers [x, y], and tiepoint [xt, yt]
        # we only preserve the full data layers, as the others cannot be placed
        cleaned_data_layer = {}
        for layer in data_layers:
            dims = data[layer].dims
            if "x" in dims and "y" in dims and len(dims) == 2:
                cleaned_name = layer
                cleaned_name = cleaned_name.replace(f"_{cur_epoch}", "")
                for pol in ["VV", "VH", "HH", "HV"]:
                    cleaned_name = cleaned_name.replace(f"_{pol}", "")

                cleaned_data_layer[cleaned_name] = layer
                if cleaned_name in [
                    "latitude", "longitude", "elevation"
                ] and mother_epoch is None:  # these are expected only at the mother
                    mother_epoch = epoch

        full_data[epoch] = {
            "data": data,
            "cleaned_data_layers": cleaned_data_layer,
            "filename": file
        }

    # sort the provided files chronologically
    sorted_epochs = list(sorted(list(full_data.keys())))

    # fallback for when mother epoch is not in the stack
    if mother_epoch is None:
        warning_msg = (
            f"Mother has not been identified. Using first epoch {sorted_epochs[0]} "
            "for metadata instead."
        )
        logger.warning(warning_msg)
        mother_epoch = sorted_epochs[0]
    daughter_epochs = [epoch for epoch in sorted_epochs if epoch != mother_epoch]

    # read metadata to find the azimuth and range coordinate offsets
    metadata_file = f"{full_data[mother_epoch]['filename']}/SNAP/product_metadata.json"
    metadata = read_metadata(metadata_file, driver="snap")

    #  Initialize stack as a Dataset
    coords = {
        "azimuth": range(
            metadata["first_line_number"],
            metadata["first_line_number"] + metadata["number_of_lines"]
        ),
        "range": range(
            metadata["first_pixel_number"],
            metadata["first_pixel_number"] + metadata["number_of_pixels"]
        ),
        "time": sorted_epochs,
    }
    ds_stack = xr.Dataset(coords=coords)

    # handle the complex data, i = real, q = complex
    slcs = None
    for epoch in sorted_epochs:
        cplx = (
            full_data[epoch]["data"][full_data[epoch]["cleaned_data_layers"]["i"]].data
            + 1j *
            full_data[epoch]["data"][full_data[epoch]["cleaned_data_layers"]["q"]].data
        )

        if slcs is None:
            slc = cplx.reshape(
                (metadata["number_of_lines"], metadata["number_of_pixels"], 1)
            )
            slcs = slc
        else:
            slc = cplx.reshape(
                (metadata["number_of_lines"], metadata["number_of_pixels"], 1)
            )
            slcs = da.concatenate([slcs, slc], axis=2)

    ds_stack = ds_stack.assign({"complex": (("azimuth", "range", "time"), slcs)})

    # retain the additional layers in the daughter znaps (which are time-variant)
    if len(daughter_epochs) > 0:
        for layer in full_data[daughter_epochs[0]]["cleaned_data_layers"].keys():
            if layer in ["i", "q"]:
                continue  # these are handled separately above
            layer_data = None
            for epoch in sorted_epochs:
                if layer_data is None:
                    if layer not in full_data[epoch]["cleaned_data_layers"].keys():
                        # e.g. it does not exist in the mother epoch, so we add zeros
                        layer_data = da.zeros(
                            (
                                metadata["number_of_lines"],
                                metadata["number_of_pixels"],
                                1
                            )
                        )
                    else:
                        layer_data = full_data[epoch]["data"][
                            full_data[epoch]["cleaned_data_layers"][layer]
                        ].data
                        layer_data = layer_data.reshape(
                            (
                                metadata["number_of_lines"],
                                metadata["number_of_pixels"],
                                1
                            )
                        )
                else:
                    if layer not in full_data[epoch]["cleaned_data_layers"].keys():
                        # e.g. it does not exist in the mother epoch, so we add zeros
                        cur_layer_data = da.zeros(
                            (
                                metadata["number_of_lines"],
                                metadata["number_of_pixels"],
                                1
                            )
                        )
                    else:
                        cur_layer_data = full_data[epoch]["data"][
                            full_data[epoch]["cleaned_layer_names"][layer]
                        ].data
                        cur_layer_data = cur_layer_data.reshape(
                            (
                                metadata["number_of_lines"],
                                metadata["number_of_pixels"],
                                1
                            )
                        )
                    layer_data = da.concatenate(
                        [layer_data, cur_layer_data], axis=2
                    )

            ds_stack = ds_stack.assign(
                {layer: (("azimuth", "range", "time"), layer_data)}
            )

    # retain the additional layers in the mother znap (which is time-invariant)
    for layer in full_data[mother_epoch]["cleaned_data_layers"].keys():
        if layer in ds_stack.data_vars.keys() or layer in ["i", "q"]:
            continue  # these are already included
        ds_stack = ds_stack.assign(
            {
                layer: (
                    ("azimuth", "range"),
                    full_data[mother_epoch]["data"][
                        full_data[mother_epoch]["cleaned_data_layers"][layer]
                    ].data
                )
            }
        )

    ds_stack = ds_stack.slcstack._get_amplitude()
    ds_stack = ds_stack.slcstack._get_phase()

    return ds_stack


def to_binary(
        output_path: str,
        data: xr.Dataset | xr.DataArray,
        data_var_name: str | None = None,
        allow_overwrite: bool = False
):
    """Write a zarr data layer to a binary file.

    The dtype and shape of the resulting binary file will be the same as the input
    data.

    Parameters
    ----------
    output_path: str
        Path to where the binary data file should be stored
    data: xr.Dataset | xr.DataArray
        Dataset or DataArray containing the data variable that should be written to
        the binary data file. If `data` is an `xr.Dataset`, the argument
        `data_var_name` is required to indicate which data variable should be written.
    data_var_name: str | None
        Name of the data variable that should be written to the binary file. Only used
        if `data` is an `xr.Dataset`, otherwise ignored. Default is `None`
    allow_overwrite: bool
        Whether or not to allow overwriting the file specified by `output_path` when
        that file already exists. If `output_path` exists and `allow_overwrite=False`,
        an OSError is raised. If `output_path` exists and `allow_overwrite=True`, the
        file in `output_path` is overwritten. If `output_path` does not exist, this
        input argument is ignored. Default is `False`

    Raises
    ------
    ValueError
        - When `data` is an `xr.Dataset` but `data_var_name` is `None`
        - When `data` is not an `xr.Dataset` or `xr.DataArray`

    KeyError
        When `data` is an `xr.Dataset` and `data_var_name` is not a data variable in 
        `data`

    OSError
        When `output_path` exists and `allow_overwrite` is set to `False`

    """
    if os.path.exists(output_path) and not allow_overwrite:
        raise OSError("Requested output file exists and overwriting is not allowed!")

    if isinstance(data, xr.Dataset):
        if data_var_name is not None:
            datalayer = xr.DataArray(data[data_var_name])
        else:
            raise ValueError("Dataset provided but layer_name is None!")
    elif isinstance(data, xr.DataArray):
        datalayer = data
    else:
        raise ValueError("data is not xr.DataArray or xr.Dataset!")

    # Create the memmap
    memmap = np.memmap(
        output_path,
        dtype=datalayer.dtype,
        mode="w+",
        shape=datalayer.shape
    )
    # Assign the data to the memmap
    memmap[:] = datalayer.data[:]
    # Save the memmap
    memmap.flush()


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
    driver: Literal["doris4", "doris5", "snap"] = "doris5",
    ifg_file_name: str = "ifgs.res",
) -> dict:
    """Read metadata of a coregistered interferogram stack.

    This function reads metadata from one or more metadata files from a coregistered
    interferogram stack, and returns the metadata as a dictionary format.

    This function supports three drivers: "doris4" for DORIS4 metadata files, e.g.
    coregistration results from TerraSAR-X; "doris5" for DORIS5 metadata files,
    e.g. coregistration results from Sentinel-1; "snap" for SNAP metadata files.
    More support for other drivers will be added in the future.

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
        "doris5" and "snap". Default is "doris5".
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
    if driver not in ["doris4", "doris5", "snap"]:
        raise NotImplementedError(
            f"Driver '{driver}' is not implemented. "
            "Supported drivers are: 'doris4', 'doris5', 'snap'."
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
        mode = "regex"
        patterns = RE_PATTERNS_DORIS5
        patterns_ifg = RE_PATTERNS_DORIS5_IFG
        array_shapes = None
    elif driver == "doris4":
        mode = "regex"
        patterns = RE_PATTERNS_DORIS4
        patterns_ifg = None
        array_shapes = None
    elif driver == "snap":
        mode = "json"
        patterns = RE_PATTERNS_SNAP
        patterns_ifg = None
        array_shapes = META_ARRAY_SHAPES_SNAP

    # Read common metadata patterns
    results = {}
    if mode == "regex":
        # Open the file
        with open(file) as f:
            content = f.read()

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
                        match = re.search(pattern, content_ifg)
                        if match:
                            results[key] = match.group(1)
                        else:
                            results[key] = None
    elif mode == "json":
        # Open the file
        with open(file) as f:
            content = json.load(f)

        raw_results = _flatten_snap_json_metadata(content)
        raw_keys = [key for key in raw_results.keys()]
        for key, pattern in patterns.items():
            matches = list(filter(re.compile(pattern).match, raw_keys))
            if len(matches) == 1:
                results[key] = raw_results[matches[0]]
            else:
                results[key] = [raw_results[match] for match in matches]
                if key in array_shapes.keys():
                    fixed_dims = [dim for dim in array_shapes[key] if dim != "auto"]
                    auto_dim = len(results[key]) // np.prod(fixed_dims)
                    if len(results[key]) % auto_dim != 0:
                        raise ValueError(
                            f"{len(results[key])} items do not fit in an array of "
                            f"shape {array_shapes[key]} for key {key}."
                        )
                    fixed_dims.insert(array_shapes[key].index("auto"), auto_dim)
                    results[key] = np.array(results[key]).reshape(tuple(fixed_dims))

    return results


def _flatten_snap_json_metadata(content: dict | list, cur_keys: tuple = ()):
    """Extract all values in a nested dict/list into a dict with as key the path."""
    all_values = []
    if isinstance(content, list):
        for key in range(len(content)):
            cur_keys_loop = cur_keys + (str(key), )
            part_values = _flatten_snap_json_metadata(content[key], cur_keys_loop)
            all_values = [*all_values, *part_values]
    elif isinstance(content, dict):
        if "data" in content.keys():  # we have hit a data entry
            if content["data"]["type"] == "utc":  # in MJD
                val = datetime(2000, 1, 1) + timedelta(
                    days=content["data"]["elems"][0],
                    seconds=content["data"]["elems"][1],
                    microseconds=content["data"]["elems"][2],
                )
                val = val.timestamp()
            elif len(content["data"]["elems"]) == 1:
                val = content["data"]["elems"][0]
            else:
                val = content["data"]["elems"]
            cur_keys_save = cur_keys + (content["name"], )
            all_values.append([val, cur_keys_save])

        else:
            cur_keys_loop = cur_keys + (content["name"], )
            if "elements" in content.keys():
                cur_keys_loop_el = cur_keys_loop + ("elements", )
                part_values = _flatten_snap_json_metadata(
                    content["elements"], cur_keys_loop_el
                )
                all_values = [*all_values, *part_values]
            if "attributes" in content.keys():
                cur_keys_loop_at = cur_keys_loop + ("attributes", )
                part_values = _flatten_snap_json_metadata(
                    content["attributes"], cur_keys_loop_at
                )
                all_values = [*all_values, *part_values]

    if cur_keys != ():  # we're still in a recursive call
        return all_values
    results = {}
    for val in all_values:
        results[".".join(val[1])] = val[0]
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
    elif driver == "snap":
        time_format = TIME_FORMAT_SNAP
        unit_conversions = META_UNIT_CONVERSION_MULTIPLICATION_KEYS_SNAP

    list_time = []
    for time in metadata[TIME_STAMP_KEY]:
        try:
            if time_format == "timestamp":  # SNAP returns timestamps
                dt = datetime.fromtimestamp(time)
            else:
                dt = datetime.strptime(time, time_format)
            list_time.append(np.datetime64(dt).astype("datetime64[ns]"))
        except ValueError as e:
            raise ValueError(
                f"Invalid date format for key: '{TIME_STAMP_KEY}'. "
                f"Expected format is '{time_format}', got {time}."
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
                if META_ARRAY_KEYS[key] is str:
                    regulated_array = np.zeros(
                        (len(arr), len(arr[0])), dtype=np.dtypes.StringDType
                    )
                else:
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
                elif isinstance(metadata[key], int):  # in case it already is an int
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
