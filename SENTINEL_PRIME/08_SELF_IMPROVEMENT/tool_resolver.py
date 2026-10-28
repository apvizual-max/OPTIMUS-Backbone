#!/usr/bin/env python3
"""
Locate external binaries without depending on PATH inheritance.

The tesseract install taught this the hard way. Writing the directory to the
user PATH in the registry succeeds, and the binary runs perfectly from a shell
that has the updated environment - but processes launched by an agent runtime
inherit a PATH captured earlier, so `shutil.which('tesseract')` returns None in
a fresh process even though the program is installed and working.

A capability that resolves only through PATH is therefore not a capability; it
is a claim about one particular shell. This resolves in three steps, in order,
and RECORDS which step succeeded so a report can state how the binary was found
rather than only that it was found:

  1. an explicit override (SENTINEL_TESSERACT_PATH / generic <NAME>_PATH)
  2. the documented install location for this machine
  3. PATH, via shutil.which

All code/comments/messages in English.
"""
import os
import shutil
from pathlib import Path
from typing import Dict, Optional


# Documented install locations, searched only after an explicit override.
# tesseract was extracted from the UB-Mannheim NSIS installer into a
# user-writable directory because this session is not elevated and the
# installer silently no-ops without admin (exit 0, nothing written).
KNOWN_LOCATIONS: Dict[str, list] = {
    'tesseract': [
        Path(os.environ.get('LOCALAPPDATA', r'C:\Users\apviz\AppData\Local'))
        / 'TesseractOCR' / 'tesseract.exe',
        Path(r'C:\Program Files\Tesseract-OCR\tesseract.exe'),
    ],
    # npm ships as a .cmd shim next to node, and a process launched by an agent
    # runtime inherits a PATH captured before node was installed. `npm` therefore
    # resolves from an interactive PowerShell and raises FileNotFoundError from a
    # plain Python subprocess. Same failure class as tesseract, so it is resolved
    # the same way: an explicit location first, PATH only as the last resort.
    'npm': [
        Path(r'C:\Program Files\nodejs\npm.cmd'),
        Path(os.environ.get('APPDATA', r'C:\Users\apviz\AppData\Roaming'))
        / 'npm' / 'npm.cmd',
    ],
}


def resolve(name: str) -> Dict[str, Optional[str]]:
    """
    Find an external binary.

    Returns a dict with:
      found      - bool, whether an executable was located
      path       - absolute path, or None
      found_via  - 'override' | 'known_location' | 'PATH' | None
      searched   - the candidate locations that were tried
    """
    override = os.environ.get(f'SENTINEL_{name.upper()}_PATH')
    searched = []

    if override:
        searched.append(f'env override: {override}')
        candidate = Path(override)
        if candidate.is_file():
            return {'found': True, 'path': str(candidate),
                    'found_via': 'override', 'searched': searched}
        # A directory override is also accepted: <dir>/<name>.exe
        as_dir = candidate / f'{name}.exe'
        if as_dir.is_file():
            return {'found': True, 'path': str(as_dir),
                    'found_via': 'override', 'searched': searched}

    for candidate in KNOWN_LOCATIONS.get(name, []):
        searched.append(f'known location: {candidate}')
        if candidate.is_file():
            return {'found': True, 'path': str(candidate),
                    'found_via': 'known_location', 'searched': searched}

    on_path = shutil.which(name)
    searched.append(f'PATH lookup: {name}')
    if on_path:
        return {'found': True, 'path': on_path, 'found_via': 'PATH',
                'searched': searched}

    return {'found': False, 'path': None, 'found_via': None, 'searched': searched}


def configure_pytesseract() -> Dict[str, Optional[str]]:
    """
    Point pytesseract at the resolved binary.

    pytesseract resolves tesseract through PATH on its own, which is the same
    fragile assumption. Setting tesseract_cmd explicitly is what actually makes
    OCR work from a process whose PATH was inherited stale.
    """
    info = resolve('tesseract')
    if not info['found']:
        return info
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = info['path']
        info['configured'] = True
    except ImportError as exc:
        info['configured'] = False
        info['error'] = f'pytesseract not importable: {exc}'
    return info


if __name__ == '__main__':
    import json
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps({'tesseract': resolve('tesseract')}, indent=2))
