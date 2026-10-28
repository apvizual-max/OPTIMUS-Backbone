"""
verify_yaml_configs.py
======================
Validates all Hermes YAML config files parse cleanly.
Also checks for presence of critical MCP server registrations.

Usage:
    python verify_yaml_configs.py
    python verify_yaml_configs.py --check-mcp antigravity-bridge agent-browser

Exit code: 0 = all pass, 1 = errors found
"""

import yaml
import sys
import argparse
from pathlib import Path

HERMES_HOME = Path(r"C:\Users\apviz\AppData\Local\hermes")
ANTIGRAVITY_CONFIG = Path(r"C:\Users\apviz\OneDrive\Documents\Antigravity_Folder\Antigravity_Projects")

REQUIRED_MCP_SERVERS = ["agent-browser", "antigravity-bridge"]


def get_all_configs():
    configs = []
    # Root config
    root = HERMES_HOME / "config.yaml"
    if root.exists():
        configs.append(root)
    # Profile configs
    configs += list((HERMES_HOME / "profiles").glob("*/config.yaml"))
    # Snapshot configs
    configs += list((HERMES_HOME / "state-snapshots").glob("*/config.yaml"))
    return configs


def validate_config(path: Path, check_mcp: list) -> dict:
    result = {"path": path, "yaml_ok": False, "mcp_checks": {}, "errors": []}
    try:
        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        result["yaml_ok"] = True

        # Check MCP server registrations
        mcp_servers = data.get("mcp_servers", {}) if data else {}
        for server in check_mcp:
            result["mcp_checks"][server] = server in mcp_servers

    except yaml.YAMLError as e:
        result["errors"].append(f"YAML error: {e}")
    except Exception as e:
        result["errors"].append(f"Read error: {e}")

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-mcp', nargs='*', default=REQUIRED_MCP_SERVERS)
    args = parser.parse_args()

    configs = get_all_configs()
    print(f"Validating {len(configs)} config files...\n")

    all_passed = True
    yaml_errors = 0
    mcp_missing = {}

    for path in sorted(configs):
        result = validate_config(path, args.check_mcp)
        rel = path.relative_to(HERMES_HOME) if path.is_relative_to(HERMES_HOME) else path

        yaml_icon = "OK" if result["yaml_ok"] else "ERROR"
        mcp_status = " | ".join(
            f"{k}={'OK' if v else 'MISSING'}"
            for k, v in result["mcp_checks"].items()
        )
        print(f"[{yaml_icon}] {rel}")
        if mcp_status:
            print(f"       MCP: {mcp_status}")

        if not result["yaml_ok"]:
            yaml_errors += 1
            all_passed = False
            for err in result["errors"]:
                print(f"       {err}")

        for server, present in result["mcp_checks"].items():
            if not present:
                mcp_missing.setdefault(server, []).append(str(rel))
                all_passed = False

    print(f"\n{'='*60}")
    print(f"YAML errors: {yaml_errors}")
    for server, paths in mcp_missing.items():
        print(f"Missing MCP '{server}' in {len(paths)} config(s):")
        for p in paths:
            print(f"  - {p}")

    if all_passed:
        print("\nSTAGE 3: PASSED — All configs valid")
    else:
        print("\nSTAGE 3: FAILED — Fix errors above")

    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
