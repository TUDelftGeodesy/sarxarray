"""test _io.py
"""

import numpy as np
import pytest

import sarxarray
from sarxarray._io import _calc_chunksize, _unpack_complex


@pytest.fixture()
def test_slcs():
    return ["../../.debug/scene_0.binaray", "../../.debug/scene_1.binaray"]


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
        assert stack.dims == {"azimuth": 100, "range": 100, "time": 2}

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
        assert stack.dims == {"azimuth": 100, "range": 100, "time": 2}

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
        assert stack.dims == {"azimuth": 100, "range": 100, "time": 1}


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
