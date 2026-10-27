import pytest
import os
from find_test_gaps import get_context

def test_get_context(tmp_path):
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\nline11\nline12\nline13\nline14\nline15\nline16\nline17\nline18\nline19\nline20\nline21\nline22\n")

    context = get_context(str(test_file), 15)
    expected = "line6\nline7\nline8\nline9\nline10\nline11\nline12\nline13\nline14\nline15\nline16\nline17\nline18\nline19\nline20\nline21\nline22\n"
    assert context == expected

    context_start = get_context(str(test_file), 3)
    expected_start = "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\nline11\nline12\nline13\n"
    assert context_start == expected_start
