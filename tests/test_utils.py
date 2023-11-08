import numpy as np
import pytest
import xarray as xr
from dask.delayed import Delayed

from sarxarray.utils import (
    _get_chunks,
    _validate_multi_look_inputs,
    complex_coherence,
    multi_look,
)


# Create a synthetic dataarray
@pytest.fixture
def synthetic_dataarray():
    np.random.seed(0)
    complex_data = np.random.rand(10, 10, 10) + 1j * np.random.rand(10, 10, 10)
    complex_data = complex_data.astype(np.complex64)
    return xr.DataArray(
        complex_data,
        dims=("azimuth", "range", "time"),
        coords={
            "azimuth": np.arange(600, 610, 1, dtype=int),
            "range": np.arange(1400, 1410, 1, dtype=int),
            "time": np.arange(1, 11, 1, dtype=int),
        },
    )


# this class tests multi_look with dataarray. For testing with dataset, see
# test_stack.py
class TestUtilsMultiLook:
    def test_stack_multi_look_mean(self, synthetic_dataarray):
        da = synthetic_dataarray
        da_ml = multi_look(da, window_size=(2, 2), method="coarsen", statistics="mean")
        assert da_ml.azimuth.size == 5
        assert da_ml.range.size == 5
        assert da_ml.time.size == 10
        assert da_ml.attrs["multi-look"] == "coarsen-mean"
        # check the "auto" chunk
        assert da_ml.chunks == ((5,), (5,), (10,))
        # assert if the data is correctly calculated
        assert np.allclose(
            da_ml.isel(azimuth=0, range=0, time=0).values,
            np.mean(da.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values),
        )
        # assert if coordinates are correctly calculated
        assert np.allclose(
            da_ml.azimuth.values,
            np.arange(0, 5, 1),
        )
        assert np.allclose(
            da_ml.range.values,
            np.arange(0, 5, 1),
        )
        assert np.allclose(
            da_ml.time.values,
            da.time.values,
        )

    def test_stack_multi_look_median(self, synthetic_dataarray):
        da = synthetic_dataarray
        da_ml = multi_look(
            da, window_size=(2, 2), method="coarsen", statistics="median"
        )
        assert da_ml.azimuth.size == 5
        assert da_ml.range.size == 5
        assert da_ml.time.size == 10
        assert da_ml.chunks == ((5,), (5,), (10,))
        assert da_ml.attrs["multi-look"] == "coarsen-median"
        # assert if the data is correctly calculated
        assert np.allclose(
            da_ml.isel(azimuth=0, range=0, time=0).values,
            np.median(da.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values),
        )

    def test_stack_multi_look_unequal_window_sizes(self, synthetic_dataarray):
        da = synthetic_dataarray
        da_ml = multi_look(da, window_size=(2, 3), method="coarsen", statistics="mean")
        assert da_ml.azimuth.size == 5
        assert da_ml.range.size == 3
        assert da_ml.time.size == 10
        assert da_ml.chunks == ((5,), (3,), (10,))
        assert da_ml.attrs["multi-look"] == "coarsen-mean"
        # assert if the data is correctly calculated
        assert np.allclose(
            da_ml.isel(azimuth=0, range=0, time=0).values,
            np.mean(da.isel(azimuth=slice(0, 2), range=slice(0, 3), time=0).values),
        )
        # assert if coordinates are correctly calculated
        assert np.allclose(
            da_ml.azimuth.values,
            np.arange(0, 5, 1),
        )
        assert np.allclose(
            da_ml.range.values,
            np.arange(0, 3, 1),
        )
        assert np.allclose(
            da_ml.time.values,
            da.time.values,
        )

    def test_stack_multi_look_compute_false(self, synthetic_dataarray):
        da = synthetic_dataarray
        da_ml = multi_look(
            da, window_size=(2, 3), method="coarsen", statistics="mean", compute=False
        )
        # assert if da_ml is a dask.delayed object
        assert isinstance(da_ml, Delayed)

        # check if calling compute() works
        results = da_ml.compute()
        assert results.azimuth.size == 5
        assert results.range.size == 3
        assert results.time.size == 10
        assert results.chunks == ((5,), (3,), (10,))
        assert results.attrs["multi-look"] == "coarsen-mean"
        # assert if the data is correctly computed
        assert np.allclose(
            results.isel(azimuth=0, range=0, time=0).values,
            np.mean(da.isel(azimuth=slice(0, 2), range=slice(0, 3), time=0).values),
        )
        # assert if coordinates are correctly computed
        assert np.allclose(
            results.azimuth.values,
            np.arange(0, 5, 1),
        )
        assert np.allclose(
            results.range.values,
            np.arange(0, 3, 1),
        )
        assert np.allclose(
            results.time.values,
            da.time.values,
        )

    def test_validate_multilook_args(self, synthetic_dataarray):
        np_arr_bad = np.ones((3, 3))
        da_bad = synthetic_dataarray.isel(azimuth=0)  # no azimuth dimension
        window_good = (2, 3)
        window_bad = (200, 200)

        with pytest.raises(TypeError):
            _validate_multi_look_inputs(
                np_arr_bad, window_good, method="coarsen", statistics="mean"
            )

        with pytest.raises(ValueError):
            _validate_multi_look_inputs(
                da_bad, window_good, method="coarsen", statistics="mean"
            )

        with pytest.raises(ValueError):
            _validate_multi_look_inputs(
                synthetic_dataarray, window_bad, method="coarsen", statistics="mean"
            )

        with pytest.raises(ValueError):
            _validate_multi_look_inputs(
                synthetic_dataarray,
                window_good,
                method="something_bad",
                statistics="mean",
            )

        with pytest.raises(ValueError):
            _validate_multi_look_inputs(
                synthetic_dataarray,
                window_good,
                method="coarsen",
                statistics="something_bad",
            )

    def test_get_chunks(self, synthetic_dataarray):
        da = synthetic_dataarray.chunk("auto")
        with pytest.raises(ValueError):
            _get_chunks(da, (200, 200))


# Create another synthetic dataset
@pytest.fixture(scope="class")
def synthetic_dataarray_2():
    complex_data = np.random.rand(10, 10, 10) + 1j * np.random.rand(10, 10, 10)
    complex_data = complex_data.astype(np.complex64)
    return xr.DataArray(
        complex_data,
        dims=("azimuth", "range", "time"),
        coords={
            "azimuth": np.arange(600, 610, 1, dtype=int),
            "range": np.arange(1400, 1410, 1, dtype=int),
            "time": np.arange(1, 11, 1, dtype=int),
        },
    )


class TestUtilsCoherence:
    def test_complex_coherence(self, synthetic_dataarray, synthetic_dataarray_2):
        reference = synthetic_dataarray
        other = synthetic_dataarray_2
        da_co = complex_coherence(reference, other, window_size=(2, 2), compute=True)

        r_img = reference.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values
        o_img = other.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values

        # numerator = mean(R * O`) in the window
        numerator = np.mean(r_img * np.conj(o_img))

        # denominator = mean(R * R`) * mean(O * O`) in the window
        mean_r = np.mean(r_img * np.conj(r_img))
        mean_o = np.mean(o_img * np.conj(o_img))
        denominator = mean_r * mean_o

        # Eq: coherence = abs( numerator / sqrt(denominator) )
        coherence = np.abs(numerator / np.sqrt(denominator))
        print(da_co.isel(azimuth=0, range=0, time=0).values)

        # assert if the data is correctly calculated
        np.testing.assert_almost_equal(
            da_co.isel(azimuth=0, range=0, time=0).values,
            coherence,
            decimal=8,
        )

    def test_complex_coherence_compute_false(
        self, synthetic_dataarray, synthetic_dataarray_2
    ):
        reference = synthetic_dataarray
        other = synthetic_dataarray_2
        da_co = complex_coherence(reference, other, window_size=(2, 2), compute=False)

        # assert if da_co is a dask.delayed object
        assert isinstance(da_co, Delayed)

        # check if calling compute() works
        results = da_co.compute()
        assert results is not None

    def test_complex_coherence_no_time(
        self, synthetic_dataarray, synthetic_dataarray_2
    ):
        reference = synthetic_dataarray.isel(time=0)
        other = synthetic_dataarray_2.isel(time=0)
        da_co = complex_coherence(reference, other, window_size=(2, 2), compute=True)

        r_img = reference.isel(azimuth=slice(0, 2), range=slice(0, 2)).values
        o_img = other.isel(azimuth=slice(0, 2), range=slice(0, 2)).values

        # numerator = mean(R * O`) in the window
        numerator = np.mean(r_img * np.conj(o_img))

        # denominator = mean(R * R`) * mean(O * O`) in the window
        mean_r = np.mean(r_img * np.conj(r_img))
        mean_o = np.mean(o_img * np.conj(o_img))
        denominator = mean_r * mean_o

        # coherence = abs( numerator / sqrt(denominator) )
        coherence = np.abs(numerator / np.sqrt(denominator))

        # assert if the data is correctly calculated
        np.testing.assert_almost_equal(
            da_co.isel(azimuth=0, range=0).values,
            coherence,
            decimal=8,
        )

    def test_complex_coherence_bad_args(
        self, synthetic_dataarray, synthetic_dataarray_2
    ):
        reference = synthetic_dataarray
        other1 = synthetic_dataarray_2.isel(azimuth=1)
        other2 = synthetic_dataarray_2
        other2.values = np.random.rand(10, 10, 10)
        with pytest.raises(ValueError):
            complex_coherence(reference, other1, window_size=(2, 2), compute=True)
        with pytest.raises(ValueError):
            complex_coherence(reference, other2, window_size=(2, 2), compute=True)
