import json
import pytest
from pathlib import Path
from unittest.mock import patch
import sys

from extract_wayland_workflows import main, load_index, extract, render_index

def test_main_success(tmp_path, capsys):
    src = tmp_path / "src"
    src.mkdir()
    out = tmp_path / "out"

    # Create dummy files
    blob_data = b"hello world\nthis is a test\nanother workflow"
    (src / "skill-bodies.bin").write_bytes(blob_data)

    index_data = {
        "version": 1,
        "entries": {
            "a/SKILL.md": [0, 12],
            "b/SKILL.md": [12, 15]
        }
    }
    (src / "skill-bodies.offsets.json").write_text(json.dumps(index_data), encoding="utf-8")

    with patch.object(sys, 'argv', ['prog', '--src', str(src), '--out', str(out)]):
        ret = main()

    assert ret == 0

    # Verify outputs
    assert (out / "a/SKILL.md").read_text(encoding="utf-8") == "hello world\n"
    assert (out / "b/SKILL.md").read_text(encoding="utf-8") == "this is a test\n"
    assert (out / "_MANIFEST.json").exists()
    assert (out / "README.md").exists()

    captured = capsys.readouterr()
    assert "extracted 2 workflows, 0 failed" in captured.out


def test_main_failure_decode(tmp_path, capsys):
    src = tmp_path / "src"
    src.mkdir()
    out = tmp_path / "out"

    # Create dummy files with invalid utf-8
    blob_data = b"hello\xffworld"
    (src / "skill-bodies.bin").write_bytes(blob_data)

    index_data = {
        "version": 1,
        "entries": {
            "a/SKILL.md": [0, 11],
        }
    }
    (src / "skill-bodies.offsets.json").write_text(json.dumps(index_data), encoding="utf-8")

    with patch.object(sys, 'argv', ['prog', '--src', str(src), '--out', str(out)]):
        ret = main()

    assert ret == 1

    captured = capsys.readouterr()
    assert "extracted 0 workflows, 1 failed" in captured.out
    assert "FAIL" in captured.out
