"""json_diff モジュールのユニットテスト。"""

import pytest
from json_diff import _diff, _fmt_value


class TestFmtValue:
    def test_string(self):
        assert _fmt_value("hello") == '"hello"'

    def test_none(self):
        assert _fmt_value(None) == "null"

    def test_bool_true(self):
        assert _fmt_value(True) == "true"

    def test_bool_false(self):
        assert _fmt_value(False) == "false"

    def test_int(self):
        assert _fmt_value(42) == "42"

    def test_float(self):
        assert _fmt_value(3.14) == "3.14"


class TestDiff:
    def test_identical_scalars(self):
        assert _diff(1, 1) == []

    def test_scalar_change(self):
        result = _diff(1, 2, "x")
        assert len(result) == 1
        assert "x" in result[0]

    def test_dict_added_key(self):
        result = _diff({}, {"a": 1})
        assert len(result) == 1
        assert "a" in result[0]

    def test_dict_removed_key(self):
        result = _diff({"a": 1}, {})
        assert len(result) == 1
        assert "a" in result[0]

    def test_dict_changed_value(self):
        result = _diff({"a": 1}, {"a": 2})
        assert len(result) == 1

    def test_nested_dict(self):
        left = {"user": {"name": "Alice", "age": 30}}
        right = {"user": {"name": "Alice", "age": 31}}
        result = _diff(left, right)
        assert len(result) == 1
        assert "user.age" in result[0]

    def test_list_changed_element(self):
        result = _diff([1, 2, 3], [1, 9, 3])
        assert len(result) == 1
        assert "[1]" in result[0]

    def test_list_added_element(self):
        result = _diff([1, 2], [1, 2, 3])
        assert len(result) == 1
        assert "[2]" in result[0]

    def test_list_removed_element(self):
        result = _diff([1, 2, 3], [1, 2])
        assert len(result) == 1
        assert "[2]" in result[0]

    def test_type_change(self):
        result = _diff("hello", 42, "x")
        assert len(result) == 1

    def test_no_diff_complex(self):
        data = {"a": [1, {"b": True}], "c": None}
        assert _diff(data, data) == []

    def test_multiple_diffs(self):
        left = {"a": 1, "b": 2, "c": 3}
        right = {"a": 1, "b": 9, "d": 4}
        result = _diff(left, right)
        assert len(result) == 3  # b changed, c removed, d added
