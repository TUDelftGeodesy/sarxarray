"""test _io.py"""

import logging
import os

import numpy as np
import pytest
import xarray as xr

import sarxarray
from sarxarray._io import _calc_chunksize, _unpack_complex
from sarxarray.conf import (
    META_ARRAY_KEYS,
    META_FLOAT_KEYS,
    META_INT_KEYS,
    RE_PATTERNS_DORIS4,
    RE_PATTERNS_DORIS5,
    RE_PATTERNS_DORIS5_IFG,
)


# Example SLC files for testing
@pytest.fixture()
def test_slcs():
    return [
        f"{os.path.dirname(__file__)}/data/scene_0.binaray",
        f"{os.path.dirname(__file__)}/data/scene_1.binaray",
    ]


# Example metadata files DORIS4
@pytest.fixture()
def res_files_doris4():
    return [
        f"{os.path.dirname(__file__)}/data/metadata/meta_doris4/20180301/metadata.res",
        f"{os.path.dirname(__file__)}/data/metadata/meta_doris4/20180312/metadata.res",
        f"{os.path.dirname(__file__)}/data/metadata/meta_doris4/20180323/metadata.res",
    ]


# Example metadata files DORIS5
@pytest.fixture()
def res_files_doris5():
    # 20180318 misses the ifgs.res file
    # 20180312 has a wrong number of pixels (24866 instead of 24865)
    # but the metadata reader should not fail
    # a warning should be raised for the wrong number of pixels
    return [
        f"{os.path.dirname(__file__)}/data/metadata/meta_doris5/20180306/metadata.res",
        f"{os.path.dirname(__file__)}/data/metadata/meta_doris5/20180312/metadata.res",
        f"{os.path.dirname(__file__)}/data/metadata/meta_doris5/20180318/metadata.res",
    ]


class TestFromDS:
    """from_dataset in _io.py"""

    def test_from_dataset_normal(self):
        test_ds = xr.open_zarr(
            f"{os.path.dirname(__file__)}/data/zarrs/slcs_example.zarr"
        )
        slcs = sarxarray.from_dataset(test_ds)
        assert all(dim in slcs.sizes for dim in ["azimuth", "range", "time"])
        assert all(var not in slcs.variables.keys() for var in ["real", "imag"])
        assert all(
            var in slcs.variables.keys() for var in ["complex", "amplitude", "phase"]
        )

    def test_from_dataset_broken_dim(self):
        test_ds_broken_dim = xr.open_zarr(
            f"{os.path.dirname(__file__)}/data/zarrs/slcs_example_broken_dim.zarr"
        )
        with pytest.raises(ValueError):
            sarxarray.from_dataset(test_ds_broken_dim)

    def test_from_dataset_broken_vars(self):
        test_ds_broken_vars = xr.open_zarr(
            f"{os.path.dirname(__file__)}/data/zarrs/slcs_example_broken_vars.zarr"
        )
        with pytest.raises(ValueError):
            sarxarray.from_dataset(test_ds_broken_vars)


class TestFromBinary:
    """from_binary in _io.py"""

    def test_loading_vars_and_coords(self, test_slcs):
        stack = sarxarray.from_binary(
            test_slcs, (100, 100), dtype=np.complex64, chunks=(10, 10)
        )
        assert set(["complex", "amplitude", "phase"]).issubset(
            [k for k in stack.data_vars.keys()]
        )
        assert set(["azimuth", "range", "time"]).issubset(
            [k for k in stack.coords.keys()]
        )
        assert stack.sizes == {"azimuth": 100, "range": 100, "time": 2}

    def test_loading_custom_var(self, test_slcs):
        """When other var names specified, do not compute amplitude and range"""
        stack = sarxarray.from_binary(
            test_slcs,
            (100, 100),
            dtype=np.complex64,
            chunks=(10, 10),
            vlabel="other_types",
        )
        assert set(["other_types"]).issubset([k for k in stack.data_vars.keys()])
        assert not (
            set(["amplitude", "phase"]).issubset([k for k in stack.coords.keys()])
        )
        assert stack.sizes == {"azimuth": 100, "range": 100, "time": 2}

    def test_loading_chunksizes(self, test_slcs):
        stack = sarxarray.from_binary(
            test_slcs, (100, 100), dtype=np.complex64, chunks=(10, 10)
        )
        assert stack.chunks["azimuth"][0] == 10
        assert stack.chunks["range"][0] == 10

    def test_loading_larger_chunksizes(self, test_slcs):
        stack = sarxarray.from_binary(
            test_slcs, (100, 100), dtype=np.complex64, chunks=(30, 30)
        )
        assert stack.chunks["azimuth"][0] == 30
        assert stack.chunks["range"][0] == 30

    def test_loading_uneven_chunksizes(self, test_slcs):
        stack = sarxarray.from_binary(
            test_slcs, (100, 100), dtype=np.complex64, chunks=(20, 40)
        )
        assert stack.chunks["azimuth"][0] == 20
        assert stack.chunks["range"][0] == 40

    def test_loading_auto_chunksizes(self, test_slcs):
        """Testfile too small, chunksize should be the whole file"""
        stack = sarxarray.from_binary(test_slcs, (100, 100), dtype=np.complex64)
        assert stack.chunks["azimuth"][0] == 100
        assert stack.chunks["range"][0] == 100

    def test_loading_one_slc(self, test_slcs):
        stack = sarxarray.from_binary(
            [test_slcs[0]], (100, 100), dtype=np.complex64, chunks=(10, 10)
        )
        assert set(["complex", "amplitude", "phase"]).issubset(
            [k for k in stack.data_vars.keys()]
        )
        assert set(["azimuth", "range", "time"]).issubset(
            [k for k in stack.coords.keys()]
        )
        assert stack.sizes == {"azimuth": 100, "range": 100, "time": 1}


class TestUtils:
    """Utility functions in _io.py"""

    def test_unpack_complex(self):
        dtype = np.dtype([("re", np.float32), ("im", np.float32)])
        cmp = np.array((1, 2), dtype=dtype)
        cmp_unpacked = _unpack_complex(cmp)
        assert cmp_unpacked == 2j + 1

    def test_calc_chunksize_tiny(self):
        assert _calc_chunksize((100, 100), np.float32, 1) == (100, 100)
        assert _calc_chunksize((100, 100), np.float32, 2) == (100, 100)

    def test_calc_chunksize_2d_big(self):
        assert _calc_chunksize((1000000, 1000000), np.float32, 1) == (6000, 6000)
        assert _calc_chunksize((1000000, 1000000), np.float32, 2) == (8000, 4000)

    def test_calc_chunksize_1d_big(self):
        assert _calc_chunksize((1000000, 100), np.float32, 1) == (6000, 100)
        assert _calc_chunksize((1000000, 100), np.float32, 2) == (8000, 100)
        assert _calc_chunksize((100, 1000000), np.float32, 1) == (100, 6000)
        assert _calc_chunksize((100, 1000000), np.float32, 2) == (100, 4000)


class TestReadMetadata:
    """Test reading metadata from DORIS .res files"""

    def test_read_metadata_doris4(self, res_files_doris4):
        metadata = sarxarray.read_metadata(res_files_doris4, driver="doris4")
        for key in RE_PATTERNS_DORIS4.keys():
            assert key in metadata
            if key in META_FLOAT_KEYS:
                assert isinstance(metadata[key], float)
            elif key in META_INT_KEYS:
                assert isinstance(metadata[key], int)
        assert metadata["first_azimuth_time"].shape[0] == 3

    def test_read_metadata_doris5(self, res_files_doris5, caplog):
        with caplog.at_level(logging.WARNING):  # Last file has a wrong number of pixels
            # also catches the multiple orbit warning
            metadata = sarxarray.read_metadata(res_files_doris5, driver="doris5")
        for key in RE_PATTERNS_DORIS5.keys():
            assert key in metadata
            if key in META_FLOAT_KEYS:
                assert isinstance(metadata[key], float)
            elif key in META_INT_KEYS:
                assert isinstance(metadata[key], int)
            elif key in META_ARRAY_KEYS.keys():
                assert isinstance(metadata[key][0], np.ndarray)
                assert len(metadata[key]) == len(res_files_doris5)
                assert len(metadata[key][0].shape) == 2
                assert isinstance(metadata[key][0][0][0], META_ARRAY_KEYS[key])
        for key in RE_PATTERNS_DORIS5_IFG.keys():
            assert key in metadata
            if key in META_FLOAT_KEYS:
                assert isinstance(metadata[key], float)
            elif key in META_INT_KEYS:
                if key == "number_of_pixels":
                    assert len(metadata[key]) == 2  # Two values for ifg sizes
                else:
                    assert isinstance(metadata[key], int)
        assert metadata["first_azimuth_time"].shape[0] == 3

    def test_read_metadata_non_existent_driver(self, res_files_doris4):
        with pytest.raises(NotImplementedError):
            sarxarray.read_metadata(res_files_doris4, driver="non_existent")

    def test_read_metadata_doris4_onefile(self, res_files_doris4):
        metadata = sarxarray.read_metadata(res_files_doris4[0], driver="doris4")
        for key in RE_PATTERNS_DORIS4.keys():
            assert key in metadata
            if key in META_FLOAT_KEYS:
                assert isinstance(metadata[key], float)
            elif key in META_INT_KEYS:
                assert isinstance(metadata[key], int)
        assert np.isscalar(metadata["first_azimuth_time"])

    def test_read_metadata_doris5_onefile(self, res_files_doris5, caplog):
        metadata = sarxarray.read_metadata(res_files_doris5[0], driver="doris5")
        for key in RE_PATTERNS_DORIS5.keys():
            assert key in metadata
            if key in META_FLOAT_KEYS:
                assert isinstance(metadata[key], float)
            elif key in META_INT_KEYS:
                assert isinstance(metadata[key], int)
            elif key in META_ARRAY_KEYS.keys():
                assert isinstance(metadata[key], np.ndarray)
                assert len(metadata[key].shape) == 2
                assert isinstance(metadata[key][0][0], META_ARRAY_KEYS[key])
        for key in RE_PATTERNS_DORIS5_IFG.keys():
            assert key in metadata
            if key in META_FLOAT_KEYS:
                assert isinstance(metadata[key], float)
            elif key in META_INT_KEYS:
                assert isinstance(metadata[key], int)
        assert np.isscalar(metadata["first_azimuth_time"])
