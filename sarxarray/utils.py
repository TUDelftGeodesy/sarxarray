import warnings
import sarxarray
import numpy as np
import xarray as xr
import dask.delayed as delayed


def multi_look(data, window_size, method="coarsen", statistics="mean", compute=True):
    """
    Perform multi-looking on a Stack, and return a Stack.

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
    # check if azimuth, range are in the dimensions
    if not {"azimuth", "range"}.issubset(data.dims):
        raise ValueError("The data must have azimuth and range dimensions.")

    # set the chunk size
    if not data.chunks:
        chunks = {
            "azimuth": "auto",
            "range": "auto",
        }
        # check if time in the dimensions
        if "time" in data.dims:
            chunks["time"] = -1
        data = data.chunk(chunks)

    if isinstance(data, xr.Dataset):
        chunk = (data.chunks["azimuth"][0], data.chunks["range"][0])
    elif isinstance(data, xr.DataArray):
        chunk = (data.chunks[0][0], data.chunks[1][0])
    else:
        raise TypeError("The data must be an xarray.Dataset or xarray.DataArray.")

    # check if window_size is valid
    if window_size[0] > data.azimuth.size or window_size[1] > data.range.size:
        warnings.warn(
            "Window size is larger than the data size, no multi-looking is performed."
        )
        return data

    # check if window_size is smaller than chunk size
    if window_size[0] > chunk[0] or window_size[1] > chunk[1]:
        warnings.warn(
            "Window size is larger than chunk size, no multi-looking is performed."
        )
        return data

    # add new atrrs here because Delayed objects are immutable
    data.attrs["multi-look"] = f"{method}-{statistics}"

    # define custom coordinate function to define new coordinates starting
    # from 0: the inputs `reshaped` and `axis` are output of
    # `coarsen_reshape` internal function and are passed to the `coord_func`
    def _custom_coord_func(reshaped, axis):
        if axis[0] == 1 or 2:
            return np.arange(0, reshaped.shape[0], 1, dtype=int)
        else:
            return reshaped.flatten()

    match method:
        case "coarsen":
            # TODO: if boundary and size should be configurable
            multi_looked = data.coarsen(
                {"azimuth": window_size[0], "range": window_size[1]},
                boundary="trim",
                side="left",
                coord_func=_custom_coord_func,
            )
        case other:
            raise NotImplementedError

    # apply statistics
    stat_functions = {
        "mean": multi_looked.mean,
        "median": multi_looked.median,
    }
    if statistics in stat_functions:
        stat_function = stat_functions[statistics]
        if compute:
            multi_looked = stat_function(keep_attrs=True)
        else:
            multi_looked = delayed(stat_function)(keep_attrs=True)
    else:
        NotImplementedError

    # Rechunk is needed because shape of the data will be changed after
    # multi-looking
    # calculate new chunck size based on the window size and the existing
    # chunk size
    chunk = (int(np.ceil(chunk[0] / window_size[0])),
                int(np.ceil(chunk[1] / window_size[1])))

    chunks = {
        "azimuth": chunk[0],
        "range": chunk[1],
    }
    if "time" in data.dims:
        chunks["time"] = -1

    multi_looked = multi_looked.chunk(chunks)

    return multi_looked


def complex_coherence(reference: xr.DataArray, other: xr.DataArray, window_size, compute=True):
    """
    Calculate complex coherence of two images.

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
    if reference.azimuth.size != other.azimuth.size or reference.range.size != other.range.size:
        raise ValueError("The two images have different shape.")

    # check if dtype is complex
    if reference.dtype != np.complex64 or other.dtype != np.complex64:
        raise ValueError("The dtype of the two images must be complex64.")

    # calculate the numerator of the equation
    da = reference * other.conj()
    numerator = multi_look(da, window_size, method="coarsen", statistics="mean", compute=compute)

    # calculate the denominator of the equation
    da = reference * reference.conj()
    reference_mean = multi_look(da, window_size, method="coarsen", statistics="mean", compute=compute)

    da = other * other.conj()
    other_mean = multi_look(da, window_size, method="coarsen", statistics="mean", compute=compute)

    denominator = reference_mean * other_mean

    # calculate the coherence
    def _compute_coherence(numerator, denominator):
        return np.abs(numerator / np.sqrt(denominator))

    if compute:
        coherence = _compute_coherence(numerator, denominator)
    else:
        coherence = delayed(_compute_coherence)(numerator, denominator)

    return coherence