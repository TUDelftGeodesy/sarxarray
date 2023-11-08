"""test stack.py
"""
import numpy as np
import pytest
import xarray as xr
from dask.delayed import Delayed


# Create a synthetic dataset
@pytest.fixture
def synthetic_dataset():
    np.random.seed(0)
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


class TestStackSARrelated:
    def test_stack_get_amp(self, synthetic_dataset):
        ds = synthetic_dataset.slcstack._get_amplitude()
        assert ds.azimuth.size == 10
        assert ds.range.size == 10
        assert ds.time.size == 10

    def test_stack_get_phase(self, synthetic_dataset):
        ds = synthetic_dataset.slcstack._get_phase()
        assert ds.azimuth.size == 10
        assert ds.range.size == 10
        assert ds.time.size == 10

    def test_stack_mrm(self, synthetic_dataset):
        ds = synthetic_dataset.slcstack._get_amplitude()
        mrm = ds.slcstack.mrm()
        assert mrm.azimuth.size == 10
        assert mrm.range.size == 10
        assert "time" not in mrm.dims
        assert np.allclose(ds.amplitude.mean(axis=2), mrm)

    def test_amp_disp(self, synthetic_dataset):
        ds = synthetic_dataset.slcstack._get_amplitude()
        amp_disp = ds.slcstack._amp_disp()
        amp = ds.amplitude
        amp_disp_calc = amp.std(axis=2) / amp.mean(axis=2)
        assert np.allclose(amp_disp, amp_disp_calc)

    def test_stack_pointselection_all(self, synthetic_dataset):
        synthetic_dataset = synthetic_dataset.slcstack._get_amplitude()
        synthetic_dataset = synthetic_dataset.slcstack._get_phase()
        stm = synthetic_dataset.slcstack.point_selection(
            threshold=100, method="amplitude_dispersion"
        )  # select all
        assert stm.space.shape[0] == 100
        assert set([k for k in stm.coords.keys()]).issubset(
            ["time", "azimuth", "range"]
        )
        assert set([d for d in stm.data_vars.keys()]).issubset(
            ["complex", "amplitude", "phase"]
        )

    def test_stack_pointselection_some(self, synthetic_dataset):
        synthetic_dataset = synthetic_dataset.slcstack._get_amplitude()
        synthetic_dataset = synthetic_dataset.slcstack._get_phase()
        stm = synthetic_dataset.slcstack.point_selection(
            threshold=0.2, method="amplitude_dispersion"
        )  # select all
        assert stm.space.shape[0] == 4
        assert set([k for k in stm.coords.keys()]).issubset(
            ["time", "azimuth", "range"]
        )
        assert set([d for d in stm.data_vars.keys()]).issubset(
            ["complex", "amplitude", "phase"]
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
        assert ds_ml.chunks == {"azimuth": (5,), "range": (5,), "time": (10,)}
        # assert if the data is correctly calculated
        assert np.allclose(
            ds_ml.complex.isel(azimuth=0, range=0, time=0).values,
            np.mean(
                ds.complex.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values
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
        assert ds_ml.chunks == {"azimuth": (5,), "range": (5,), "time": (10,)}
        assert ds_ml.attrs["multi-look"] == "coarsen-median"
        # assert if the data is correctly calculated
        assert np.allclose(
            ds_ml.complex.isel(azimuth=0, range=0, time=0).values,
            np.median(
                ds.complex.isel(azimuth=slice(0, 2), range=slice(0, 2), time=0).values
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
        assert ds_ml.chunks == {"azimuth": (5,), "range": (3,), "time": (10,)}
        assert ds_ml.attrs["multi-look"] == "coarsen-mean"
        # assert if the data is correctly calculated
        assert np.allclose(
            ds_ml.complex.isel(azimuth=0, range=0, time=0).values,
            np.mean(
                ds.complex.isel(azimuth=slice(0, 2), range=slice(0, 3), time=0).values
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
        assert results.chunks == {"azimuth": (5,), "range": (3,), "time": (10,)}
        assert results.attrs["multi-look"] == "coarsen-mean"
        # assert if the data is correctly computed
        assert np.allclose(
            results.complex.isel(azimuth=0, range=0, time=0).values,
            np.mean(
                ds.complex.isel(azimuth=slice(0, 2), range=slice(0, 3), time=0).values
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
