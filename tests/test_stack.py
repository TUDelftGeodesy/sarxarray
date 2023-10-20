"""test stack.py
"""
import pytest
import sarxarray
from dask.delayed import Delayed
import numpy as np
import xarray as xr

# Create a synthetic dataset
@pytest.fixture
def synthetic_dataset():
    return xr.Dataset(
        {
            "complex": (
                ("azimuth", "range", "time"),
                np.random.rand(10, 10, 10) + 1j * np.random.rand(10, 10, 10),
            )
        },
        coords={
            "azimuth": np.arange(600, 610, 1, dtype=int),
            "range": np.arange(1400, 1410, 1, dtype=int),
            "time": np.arange(1, 11, 1, dtype=int),
        },
    )

class TestStackMultiLook:
    def test_stack_multi_look_mean(self, synthetic_dataset):
        ds = synthetic_dataset
        ds_ml = ds.slcstack.multi_look(
            window_size=(2, 2), method="coarsen", statistics="mean"
        )
        assert ds_ml.azimuth.size == 5
        assert ds_ml.range.size == 5
        assert ds_ml.time.size == 10
        assert ds_ml.attrs["multi-look"] == "coarsen-mean"
        # check the "auto" chunk
        assert ds_ml.chunks == {'azimuth': (5,), 'range': (5,), 'time': (10,)}
        # assert if the data is correctly calculated
        assert np.allclose(
            ds_ml.complex.isel(azimuth=0, range=0, time=0).values,
            np.mean(
                ds.complex.isel(
                    azimuth=slice(0, 2), range=slice(0, 2), time=0
                ).values
            ),
        )
        # assert if coordinates are correctly calculated
        assert np.allclose(
            ds_ml.azimuth.values,
            np.arange(0, 5, 1),
        )
        assert np.allclose(
            ds_ml.range.values,
            np.arange(0, 5, 1),
        )
        assert np.allclose(
            ds_ml.time.values,
            ds.time.values,
        )

    def test_stack_multi_look_median(self, synthetic_dataset):
        ds = synthetic_dataset
        ds_ml = ds.slcstack.multi_look(
            window_size=(2, 2), method="coarsen", statistics="median"
        )
        assert ds_ml.azimuth.size == 5
        assert ds_ml.range.size == 5
        assert ds_ml.time.size == 10
        assert ds_ml.chunks == {'azimuth': (5,), 'range': (5,), 'time': (10,)}
        assert ds_ml.attrs["multi-look"] == "coarsen-median"
        # assert if the data is correctly calculated
        assert np.allclose(
            ds_ml.complex.isel(azimuth=0, range=0, time=0).values,
            np.median(
                ds.complex.isel(
                    azimuth=slice(0, 2), range=slice(0, 2), time=0
                ).values
            ),
        )

    def test_stack_multi_look_unequal_window_sizes(self, synthetic_dataset):
        ds = synthetic_dataset
        ds_ml = ds.slcstack.multi_look(
            window_size=(2, 3), method="coarsen", statistics="mean"
        )
        assert ds_ml.azimuth.size == 5
        assert ds_ml.range.size == 3
        assert ds_ml.time.size == 10
        assert ds_ml.chunks == {'azimuth': (5,), 'range': (3,), 'time': (10,)}
        assert ds_ml.attrs["multi-look"] == "coarsen-mean"
        # assert if the data is correctly calculated
        assert np.allclose(
            ds_ml.complex.isel(azimuth=0, range=0, time=0).values,
            np.mean(
                ds.complex.isel(
                    azimuth=slice(0, 2), range=slice(0, 3), time=0
                ).values
            ),
        )
        # assert if coordinates are correctly calculated
        assert np.allclose(
            ds_ml.azimuth.values,
            np.arange(0, 5, 1),
        )
        assert np.allclose(
            ds_ml.range.values,
            np.arange(0, 3, 1),
        )
        assert np.allclose(
            ds_ml.time.values,
            ds.time.values,
        )

    def test_stack_multi_look_compute_false(self, synthetic_dataset):
        ds = synthetic_dataset
        ds_ml = ds.slcstack.multi_look(
            window_size=(2, 3), method="coarsen", statistics="mean", compute=False
        )
        # assert if ds_ml is a dask.delayed object
        assert isinstance(ds_ml, Delayed)

        # check if calling compute() works
        results = ds_ml.compute()
        assert results.azimuth.size == 5
        assert results.range.size == 3
        assert results.time.size == 10
        assert results.chunks == {'azimuth': (5,), 'range': (3,), 'time': (10,)}
        assert results.attrs["multi-look"] == "coarsen-mean"
        # assert if the data is correctly computed
        assert np.allclose(
            results.complex.isel(azimuth=0, range=0, time=0).values,
            np.mean(
                ds.complex.isel(
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
            ds.time.values,
        )


# Create a other synthetic dataset
@pytest.fixture(scope="class")
def synthetic_dataset_2():
    return xr.Dataset(
        data_vars={
            "complex": (
                ("azimuth", "range", "time"),
                np.random.rand(10, 10, 10) + 1j * np.random.rand(10, 10, 10),
            )
        },
        coords={
            "azimuth": np.arange(600, 610, 1, dtype=int),
            "range": np.arange(1400, 1410, 1, dtype=int),
            "time": np.arange(1, 11, 1, dtype=int),
        },
    )

class TestStackCoherence:
    def test_complex_coherence(self, synthetic_dataset, synthetic_dataset_2):
        ds = synthetic_dataset
        ds_2 = synthetic_dataset_2
        ds_co = ds.slcstack.complex_coherence(ds_2, window_size=(2, 2), compute=True)

        R_img = ds.complex.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values
        O_img = ds_2.complex.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values

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
            ds_co.complex.isel(azimuth=0, range=0, time=0).values,
            coherence,
            decimal=8,
        )
