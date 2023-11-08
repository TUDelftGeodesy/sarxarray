import numpy as np
import xarray as xr
from dask.delayed import Delayed, delayed


def multi_look(data, window_size, method="coarsen", statistics="mean", compute=True):
    """Perform multi-looking on a Stack, and return a Stack.

    Parameters
    ----------
    data : xarray.Dataset or xarray.DataArray
        The data to be multi-looked.
    window_size : tuple
        Window size for multi-looking, in the format of (azimuth, range)
    method : str, optional
        Method of multi-looking, by default "coarsen"
    statistics : str, optional
        Statistics method for multi-looking, by default "mean"
    compute : bool, optional
        Whether to compute the result, by default True. If False, the result
        will be `dask.delayed.Delayed`. This is useful when the multi_look
        is used as an intermediate result.

    Returns
    -------
    xarray.Dataset or xarray.DataArray
        An `xarray.Dataset` or `xarray.DataArray` with coarsen shape if
        `compute` is True, otherwise a `dask.delayed.Delayed` object.
    """
    # validate the input
    _validate_multi_look_inputs(data, window_size, method, statistics)

    # chunk data if not already chunked
    if isinstance(data, Delayed) or not data.chunks:
        data = data.chunk("auto")

    # get the chunk size
    if isinstance(data, Delayed):
        chunks = "auto"
    else:
        chunks = _get_chunks(data, window_size)

    # add new atrrs here because Delayed objects are immutable
    data.attrs["multi-look"] = f"{method}-{statistics}"

    # define custom coordinate function to define new coordinates starting
    # from 0: the inputs `reshaped` and `axis` are output of
    # `coarsen_reshape` internal function and are passed to the `coord_func`
    def _custom_coord_func(reshaped, axis):
        if axis[0] == 1 or axis[0] == 2:
            return np.arange(0, reshaped.shape[0], 1, dtype=int)
        else:
            return reshaped.flatten()

    if method == "coarsen":
        # TODO: if boundary and size should be configurable
        multi_looked = data.coarsen(
            {"azimuth": window_size[0], "range": window_size[1]},
            boundary="trim",
            side="left",
            coord_func=_custom_coord_func,
        )

    # apply statistics
    stat_functions = {
        "mean": multi_looked.mean,
        "median": multi_looked.median,
    }

    stat_function = stat_functions[statistics]
    if compute:
        multi_looked = stat_function(keep_attrs=True)
    else:
        multi_looked = delayed(stat_function)(keep_attrs=True)

    # Rechunk is needed because shape of the data will be changed after
    # multi-looking
    multi_looked = multi_looked.chunk(chunks)

    return multi_looked


def complex_coherence(
    reference: xr.DataArray, other: xr.DataArray, window_size, compute=True
):
    """Calculate complex coherence of two images.

    Assume two images reference (R) and other (O), the complex coherence is
    defined as:
    numerator = mean(R * O`) in a window
    denominator = mean(R * R`) * mean(O * O`) in a window
    coherence = abs( numerator / sqrt(denominator) ),
    See the equationin chapter 28 in http://doris.tudelft.nl/software/doris_v4.02.pdf

    Parameters
    ----------
    reference : xarray.DataArray
        The reference image to calculate complex coherence with.
    other : xarray.DataArray
        The other image to calculate complex coherence with.
    window_size : tuple
        Window size for multi-looking, in the format of (azimuth, range)
    compute : bool, optional
        Whether to compute the result, by default True. If False, the result
        will be `dask.delayed.Delayed`. This is useful when the complex_coherence
        is used as an intermediate result.

    Returns
    -------
    xarray.DataArray
        An `xarray.DataArray` if `compute` is True,
        otherwise a `dask.delayed.Delayed` object.
    """
    # check if the two images have the same shape
    if (
        reference.azimuth.size != other.azimuth.size
        or reference.range.size != other.range.size
    ):
        raise ValueError("The two images have different shape.")

    # check if dtype is complex
    if reference.dtype != np.complex64 or other.dtype != np.complex64:
        raise ValueError("The dtype of the two images must be complex64.")

    # calculate the numerator of the equation
    da = reference * other.conj()
    numerator = multi_look(
        da, window_size, method="coarsen", statistics="mean", compute=compute
    )

    # calculate the denominator of the equation
    da = reference * reference.conj()
    reference_mean = multi_look(
        da, window_size, method="coarsen", statistics="mean", compute=compute
    )

    da = other * other.conj()
    other_mean = multi_look(
        da, window_size, method="coarsen", statistics="mean", compute=compute
    )

    denominator = reference_mean * other_mean

    # calculate the coherence
    def _compute_coherence(numerator, denominator):
        return np.abs(numerator / np.sqrt(denominator))

    if compute:
        coherence = _compute_coherence(numerator, denominator)
    else:
        coherence = delayed(_compute_coherence)(numerator, denominator)

    return coherence


def _validate_multi_look_inputs(data, window_size, method, statistics):
    # check if data is xarray
    if not isinstance(data, xr.Dataset | xr.DataArray):
        raise TypeError("The data must be an xarray.Dataset or xarray.DataArray.")

    # check if azimuth, range are in the dimensions
    if not {"azimuth", "range"}.issubset(data.dims):
        raise ValueError("The data must have azimuth and range dimensions.")

    # check if window_size is valid
    if window_size[0] > data.azimuth.size or window_size[1] > data.range.size:
        raise ValueError("Window size is larger than data size.")

    # check if method is valid
    if method not in ["coarsen"]:
        raise ValueError("The method must be one of ['coarsen'].")

    # check if statistics is valid
    if statistics not in ["mean", "median"]:
        raise ValueError("The statistics must be one of ['mean', 'median'].")


def _get_chunks(data, window_size):
    if isinstance(data, xr.Dataset):
        chunks = {
            "azimuth": data.chunks["azimuth"][0],
            "range": data.chunks["range"][0],
        }
        if "time" in data.dims:
            chunks["time"] = data.chunks["time"][0]
    elif isinstance(data, xr.DataArray):
        chunks = {"azimuth": data.chunks[0][0], "range": data.chunks[1][0]}
        if "time" in data.dims:
            chunks["time"] = data.chunks[2][0]

    # check if window_size is smaller than chunks size
    if window_size[0] > chunks["azimuth"] or window_size[1] > chunks["range"]:
        raise ValueError(
            f"Window size ({window_size}) should be smaller than chunk size ({chunks})"
        )

    # calculate new chunck size based on the window size and the existing chunk
    # size
    chunks["azimuth"] = int(np.ceil(chunks["azimuth"] / window_size[0]))
    chunks["range"] = int(np.ceil(chunks["range"] / window_size[1]))

    return chunks
