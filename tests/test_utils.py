import pytest
from dask.delayed import Delayed
import numpy as np
import xarray as xr
from sarxarray.utils import multi_look, complex_coherence

# Create a synthetic dataarray
@pytest.fixture
def synthetic_dataarray():
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
            np.mean(
                da.isel(
                    azimuth=slice(0, 2), range=slice(0, 2), time=0
                ).values
            ),
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
        da_ml = multi_look(da, window_size=(2, 2), method="coarsen", statistics="median")
        assert da_ml.azimuth.size == 5
        assert da_ml.range.size == 5
        assert da_ml.time.size == 10
        assert da_ml.chunks == ((5,), (5,), (10,))
        assert da_ml.attrs["multi-look"] == "coarsen-median"
        # assert if the data is correctly calculated
        assert np.allclose(
            da_ml.isel(azimuth=0, range=0, time=0).values,
            np.median(
                da.isel(
                    azimuth=slice(0, 2), range=slice(0, 2), time=0
                ).values
            ),
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
            np.mean(
                da.isel(
                    azimuth=slice(0, 2), range=slice(0, 3), time=0
                ).values
            ),
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
        da_ml = multi_look(da, window_size=(2, 3), method="coarsen", statistics="mean", compute=False)
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
            np.mean(
                da.isel(
                    azimuth=slice(0, 2), range=slice(0, 3), time=0
                ).values
            ),
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

        R_img = reference.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values
        O_img = other.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values

        # numerator = mean(R * O`) in the window
        numerator = np.mean( R_img * np.conj(O_img) )

        # denominator = mean(R * R`) * mean(O * O`) in the window
        mean_R = np.mean( R_img * np.conj(R_img) )
        mean_O = np.mean( O_img * np.conj(O_img) )
        denominator = mean_R * mean_O

        # coherence = abs( numerator / sqrt(denominator) )
        coherence = np.abs(numerator / np.sqrt(denominator))

        # assert if the data is correctly calculated
        np.testing.assert_almost_equal(
            da_co.isel(azimuth=0, range=0, time=0).values,
            coherence,
            decimal=8,
        )

    def test_complex_coherence_compute_false(self, synthetic_dataarray, synthetic_dataarray_2):
        reference = synthetic_dataarray
        other = synthetic_dataarray_2
        da_co = complex_coherence(reference, other, window_size=(2, 2), compute=False)

        # assert if da_co is a dask.delayed object
        assert isinstance(da_co, Delayed)

        # check if calling compute() works
        results = da_co.compute()
        assert results is not None
