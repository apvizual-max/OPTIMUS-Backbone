import pytest
from pathlib import Path
import json
import hashlib
from scripts.extract_wayland_workflows import extract, render_index

def test_extract(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    out = tmp_path / "out"

    # Create fake blob and index
    blob_data = b"hello world\nthis is a test\x80bad utf8"
    (src / "skill-bodies.bin").write_bytes(blob_data)

    index_data = {
        "version": "1.0",
        "entries": {
            "hello.txt": [0, 11],
            "nested/test.txt": [12, 14],
            "bad.txt": [26, 8]
        }
    }
    (src / "skill-bodies.offsets.json").write_text(json.dumps(index_data), encoding="utf-8")

    manifest = extract(src, out)

    assert manifest["source"] == str(src)
    assert manifest["output"] == str(out)
    assert manifest["blob_bytes"] == len(blob_data)
    assert manifest["index_version"] == "1.0"
    assert manifest["extracted"] == 2
    assert manifest["failed"] == 1

    assert (out / "hello.txt").read_text(encoding="utf-8") == "hello world"
    assert (out / "nested/test.txt").read_text(encoding="utf-8") == "this is a test"

    assert not (out / "bad.txt").exists()

    assert json.loads((out / "_MANIFEST.json").read_text(encoding="utf-8")) == manifest

def test_render_index():
    manifest = {
        "source": "src_path",
        "output": "out_path",
        "blob_bytes": 1024,
        "extracted": 2,
        "failed": 0,
        "workflows": [
            {"path": "category/skill1/SKILL.md", "bytes": 500, "sha256": "1234abcd"},
            {"path": "skill2.md", "bytes": 524, "sha256": "5678efgh"}
        ]
    }

    index_text = render_index(manifest)

    assert "**Source**: `src_path`" in index_text
    assert "**Output**: `out_path`" in index_text
    assert "1,024-byte packed blob" in index_text
    assert "`skill1` | 500 | `1234abcd`" in index_text
    assert "`skill2.md` | 524 | `5678efgh`" in index_text
