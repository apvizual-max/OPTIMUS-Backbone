import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from minimax_hermes_bridge import HermesBridge
import os
import yaml

@pytest.fixture
def mock_hermes_home(tmp_path):
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    return hermes_home

def test_h_enforce_no_yaml_installed(mock_hermes_home):
    # Simulate yaml not being installed
    bridge = HermesBridge()
    with patch.dict('sys.modules', {'yaml': None}):
        result = bridge.h_enforce({})

    assert result.severity == "fail"
    assert "PyYAML not installed" in result.title

def test_h_enforce_no_config_file(mock_hermes_home):
    bridge = HermesBridge()
    with patch('minimax_hermes_bridge.HERMES_HOME', mock_hermes_home):
        # config.yaml doesn't exist yet
        result = bridge.h_enforce({})

    assert result.severity == "fail"
    assert "config.yaml missing" in result.title

def test_h_enforce_no_changes_needed(mock_hermes_home):
    bridge = HermesBridge()
    config_file = mock_hermes_home / "config.yaml"

    # Create config.yaml with correct enforcement
    initial_config = {
        "enforcement": {
            "enabled": True,
            "guardian_strict": True,
            "trigger_detection": True,
            "auto_recalibrate": True
        }
    }
    with open(config_file, "w") as f:
        yaml.safe_dump(initial_config, f)

    with patch('minimax_hermes_bridge.HERMES_HOME', mock_hermes_home):
        result = bridge.h_enforce({})

    assert result.severity == "ok"
    assert "already correct" in result.title

def test_h_enforce_fixes_missing_enforcement(mock_hermes_home):
    bridge = HermesBridge()
    config_file = mock_hermes_home / "config.yaml"

    # Create config.yaml without enforcement
    with open(config_file, "w") as f:
        yaml.safe_dump({"some_other_key": "value"}, f)

    with patch('minimax_hermes_bridge.HERMES_HOME', mock_hermes_home):
        result = bridge.h_enforce({})

    assert result.severity == "ok"
    assert "healed" in result.title

    # Check that it actually fixed the file
    with open(config_file, "r") as f:
        new_config = yaml.safe_load(f)

    assert "enforcement" in new_config
    enf = new_config["enforcement"]
    assert enf["enabled"] is True
    assert enf["guardian_strict"] is True
    assert enf["trigger_detection"] is True
    assert enf["auto_recalibrate"] is True

def test_h_enforce_fixes_incorrect_enforcement(mock_hermes_home):
    bridge = HermesBridge()
    config_file = mock_hermes_home / "config.yaml"

    # Create config.yaml with incorrect enforcement
    initial_config = {
        "enforcement": {
            "enabled": False,
            "guardian_strict": False,
            "trigger_detection": True, # This one is correct
            "auto_recalibrate": False
        }
    }
    with open(config_file, "w") as f:
        yaml.safe_dump(initial_config, f)

    with patch('minimax_hermes_bridge.HERMES_HOME', mock_hermes_home):
        result = bridge.h_enforce({})

    assert result.severity == "ok"
    assert "healed" in result.title
    assert all(k in result.evidence["changed"] for k in ["enabled", "guardian_strict", "auto_recalibrate"])
    assert "trigger_detection" not in result.evidence["changed"]

    # Check that it actually fixed the file
    with open(config_file, "r") as f:
        new_config = yaml.safe_load(f)

    enf = new_config["enforcement"]
    assert enf["enabled"] is True
    assert enf["guardian_strict"] is True
    assert enf["trigger_detection"] is True
    assert enf["auto_recalibrate"] is True
