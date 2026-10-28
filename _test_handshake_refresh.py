# -*- coding: utf-8 -*-
"""Test de regresie: handshake-ul MCP trebuie sa fie pe bucla de refresh.

Context masurat: limita de prospetime a verificarii `mcp_tools_wired` este de
24 de ore. Inregistrarea se scria la mana, o singura data, si apoi imbatranea -
pana cand doua verificari din suita cadeau in rosu si nu exista nimic in sistem
care sa poata reactiona. Limita era un termen pe care doar un om il putea
respecta.

Recepta testului:
  1. conectat   - blocul worker-ului apeleaza scriptul de handshake
  2. la timp    - perioada calculata e in interiorul limitei de 24h
  3. discrimina - aceeasi verificare, peste o copie fara handshake, raporteaza
                   "neconectat". Daca raporteaza la fel, testul nu masoara
                   nimic.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(ROOT, "13_COMMAND_CENTER", "api", "server.ps1")

# Limita pe care o aplica monitorul pentru mcp_tools_wired, in secunde.
BOUND_SECONDS = 86400
# Perioada pe care o urmarim: o ora, mult in interiorul limitei.
TARGET_PERIOD = 3600


def check(name, ok, message, detail=""):
    print("  [%s]   %s: %s" % ("ok" if ok else "FAIL", name, message))
    if not ok:
        if detail:
            print("           %s" % detail)
    return bool(ok)


def _worker_block(text):
    """Blocul Start-Job: de la Start-Job pana la linia care inchide jobul."""
    start = text.find("$worker = Start-Job")
    if start < 0:
        return ""
    end = text.find("\ntry {", start)
    return text[start:end if end > 0 else len(text)]


def _is_wired(block):
    """Acelasi predicat, aplicat blocului real sau unei copii neutralizate."""
    if not block:
        return False
    return ("mcp_handshake.py" in block
            and re.search(r"&\s*\$pyExe\s+\$handshakeScript", block) is not None)


def main():
    with io.open(SERVER, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    block = _worker_block(src)

    results = []
    results.append(check(
        "handshake_refresh_is_wired", _is_wired(block),
        "the refresh worker calls mcp_handshake.py",
        "the worker block does not invoke the handshake script"))

    # Perioada: o sa fie calculata din perioada de refresh, nu scrisa fix.
    m = re.search(r"\$handshakeEvery\s*=\s*\[Math\]::Max\(1,\s*"
                  r"\[int\]\[Math\]::Floor\((\d+)\s*/", block)
    results.append(check(
        "handshake_refresh_period_inside_bound",
        m is not None and int(m.group(1)) <= TARGET_PERIOD,
        "the cadence is computed from the refresh period, target %ds "
        "(bound %ds)" % (TARGET_PERIOD, BOUND_SECONDS),
        "no computed handshake period found in the worker block"))

    # Control de sensibilitate: aceeasi verificare, peste o copie fara
    # handshake, trebuie sa raporteze neconectat.
    broken = block.replace("mcp_handshake.py", "mcp_handshake.py.REMOVED")
    control_ok = (not _is_wired(broken)) if broken != block else False
    results.append(check(
        "handshake_refresh_control_discriminates", control_ok,
        "the same predicate reports 'not wired' on a copy with the handshake "
        "removed, so this check is measuring the gate and not passing vacuously",
        "the neutralised copy still looked wired, so this test proves nothing"))

    print("  ----")
    print("  %d/%d checks passed" % (sum(1 for r in results if r), len(results)))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
