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
            "azimuth": np.arange(10),
            "range": np.arange(10),
            "time": np.arange(10),
        },
    )

class TestStackMultiLook:
    def test_stack_multi_look_mean(self, synthetic_dataset):
        ds = synthetic_dataset
        ds_ml = ds.slcstack.multi_look(
            window_size=(2, 2), method="coarsen", statistics="mean", chunk=100
        )
        assert ds_ml.azimuth.size == 5
        assert ds_ml.range.size == 5
        assert ds_ml.time.size == 10
        assert ds_ml.chunks == {'azimuth': (5,), 'range': (5,), 'time': (10,)}
        assert ds_ml.attrs["multi-look"] == "coarsen-mean"
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
        assert ds_ml.azimuth.values[0] == np.mean(ds.azimuth.isel(azimuth=slice(0, 2)).values)
        assert ds_ml.range.values[0] == np.mean(ds.range.isel(range=slice(0, 2)).values)
        assert np.allclose(
            ds_ml.time.values,
            ds.time.values,
        )

    def test_stack_multi_look_median(self, synthetic_dataset):
        ds = synthetic_dataset
        ds_ml = ds.slcstack.multi_look(
            window_size=(2, 2), method="coarsen", statistics="median", chunk=100
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
            window_size=(2, 3), method="coarsen", statistics="mean", chunk=100
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
        assert ds_ml.azimuth.values[0] == np.mean(ds.azimuth.isel(azimuth=slice(0, 2)).values)
        assert ds_ml.range.values[0] == np.mean(ds.range.isel(range=slice(0, 3)).values)
        assert np.allclose(
            ds_ml.time.values,
            ds.time.values,
        )

    def test_stack_multi_look_compute_false(self, synthetic_dataset):
        ds = synthetic_dataset
        ds_ml = ds.slcstack.multi_look(
            window_size=(2, 3), method="coarsen", statistics="mean", chunk=100, compute=False
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
        assert results.azimuth.values[0] == np.mean(ds.azimuth.isel(azimuth=slice(0, 2)).values)
        assert results.range.values[0] == np.mean(ds.range.isel(range=slice(0, 3)).values)
        assert np.allclose(
            results.time.values,
            ds.time.values,
        )
