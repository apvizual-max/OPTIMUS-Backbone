<!-- SOT-STATUS-BANNER
  Added 2026-10-02 10:46 by scripts\stamp-doc-status.ps1

  THIS IS A POINT-IN-TIME DOCUMENT: the diagnosis of the Hermes relaunch-loop / venv-sync defect that has since been FIXED.

  It is deliberately NOT rewritten -- rewriting it would destroy the record of
  what was true when it was written. For the CURRENT system state read:

    POPY_MiniMax_OPTIMUS_Status_Report-10-02-2026.md   <- current state, for Popy
    mavis-minimax-optimus-system                        <- skill: restore + config SOT
    mavis-minimax-index-folder-update                   <- skill: how to index this folder
    optimus status   /  cc start   /  cc guard          <- live truth, measured
-->
# Hermes `update` infinite relaunch loop — defect report

**Reported:** 2026-10-02
**Component:** `hermes_cli/venv_sync.py` → `prepare_launch()`
**Severity:** high — every non-metadata CLI invocation hangs until the user force-quits
**Platform observed:** Windows 11 (10.0.26100 x64), Python 3.14.7, `updateMechanism: "self"`, git checkout install

---

## 1. Symptom

`hermes update` (or any command that is not `pm …` and not `-h/--help/-V/--version`) never
returns. It prints one warning per recursion level and spawns a nested child process each
time, growing the process tree without bound:

```
hermes: a source update could not be finished automatically (6 attempts); run `hermes update` from a shell to finish it
hermes: a source update could not be finished automatically (6 attempts); run `hermes update` from a shell to finish it
hermes: a source update could not be finished automatically (6 attempts); run `hermes update` from a shell to finish it
... (7 observed levels)
```

Each `Ctrl+C` raises `KeyboardInterrupt` one level deeper:

```
Traceback (most recent call last):
  ...
  File "...\hermes-agent\hermes_bootstrap.py", line 548, in <module>
    raise RelaunchExit(subprocess.call(_command))
  ...
  File "...\subprocess.py", line 1605, in _wait
    result = _winapi.WaitForSingleObject(self._handle, timeout_millis)
KeyboardInterrupt
```

The identical warning is repeated at every level because each child re-enters the same code
with the same state. Note that the traceback frames come from the *parent* waiting on the
*child*, which is what makes the nesting visible.

`hermes --version` and any `hermes pm …` command still work — they short-circuit before
the affected code (see §3).

## 2. Preconditions

1. A source update has moved the checkout to a commit whose `pyproject.toml` / `uv.lock`
   no longer matches the recorded dependency generation, so
   `pm.venv_is_current(project_root=root)` returns **False**.
2. The post-update tail has failed often enough to exhaust the retry budget:
   `installs/<key>/source-completion-attempts` contains `6`, and
   `COMPLETION_RETRY_MAX_ATTEMPTS == 6` (`venv_sync.py:188`).
   `completion_retry_state()` therefore returns `(may_retry=False, 6, 0)` (`venv_sync.py:233-234`).

Once both hold, the state is **self-sustaining**: nothing in this path can ever set
`current` back to `True`, and the relaunch is unconditional.

## 3. Root cause

`prepare_launch()` bounds the *sync* but not the *relaunch*.

The give-up branch warns and then falls through:

```python
# venv_sync.py:358-372
_may_retry, _attempts, _backoff = completion_retry_state(root)
if not _may_retry and _attempts >= COMPLETION_RETRY_MAX_ATTEMPTS:
    # "Leave the marker for an explicit `hermes update`; say so once."
    print(f"hermes: a source update could not be finished automatically "
          f"({_attempts} attempts); run `hermes update` from a shell to finish it",
          file=sys.stderr, flush=True)
elif not _may_retry:
    pass                                    # backoff window not elapsed
elif not owed_to_cli and (not current or pending.is_file()):
    ...                                     # sync / finish the tail
```

Because `_may_retry` is `False`, the `elif` that performs the repair is unreachable — the
install is left out of date on purpose. But execution then continues to:

```python
# venv_sync.py:393-404
python = resolve_store_python(root)
if python is None:
    raise RuntimeError("source update has no managed Python; run `hermes pm install`")
same = os.path.normcase(os.path.abspath(python)) == os.path.normcase(os.path.abspath(sys.executable))
if not current or not same:                 # <-- `not current` is still True
    publish_launchers(root)
    return python                           # <-- relaunch, unconditionally
```

`not current` is precisely the condition the give-up branch declined to fix, so the process
relaunches. The relaunched child evaluates the same state, reaches the same conclusion, and
relaunches again. On POSIX this is `os.execv`; on Windows it is
`subprocess.call` + `RelaunchExit` (`hermes_bootstrap.py:545-549`), which is what produces
the nested traceback.

The comment above the cap states the intent:

> "The tail has failed often enough that every relaunch re-running it does more harm than
> good (#122206: 'every launch burns ~4 minutes')."

Bounding the tail converted a slow-but-terminating repair into a fast unbounded relaunch,
which is strictly worse and does not match the stated intent.

### Why `--version` and `pm …` still work

Both bypass `prepare_launch` before the affected code:

```python
# venv_sync.py:336-341
if (command_argv(argv)[:1] == ["pm"]
        or _METADATA_FLAGS & set(argv)
        or os.environ.get("HERMES_DISABLE_LAZY_INSTALLS", "").lower() in ("1", "true", "yes")
        or not (root / ".git").exists()
        or not (root / "pyproject.toml").is_file()):
    return None
```

plus the stdlib-only fast path for repair:

```python
# hermes_bootstrap.py:533
_pm_repair = command_argv(sys.argv[1:])[:2] == ["pm", "repair"]
```

This makes the failure look partial, which complicates triage.

## 4. Suggested fix

Make the relaunch respect the retry budget, so an exhausted budget is terminal for that
launch rather than recursive:

```python
# venv_sync.py:402
if (not current or not same) and (_may_retry or current is False and _attempts == 0):
    ...
```

Cleaner, and closest to the stated intent — bound the relaunch explicitly rather than
inferring it:

```python
# venv_sync.py:358-404 (sketch)
if not _may_retry and _attempts >= COMPLETION_RETRY_MAX_ATTEMPTS:
    print(... "could not be finished automatically" ..., file=sys.stderr, flush=True)
    # Fall back to the previous dependency generation instead of re-entering
    # this same decision. Everything below assumes a repair is still owed.
    return None
```

Returning `None` here degrades to the documented behaviour already implemented further down
("Degrade, never brick the CLI: … an offline or half-finished update leaves a usable Hermes
plus a warning", `hermes_bootstrap.py:554-560`): the previous dependency generation is still
selected, the user sees one actionable warning, and an explicit `hermes update` from a shell
remains the remedy — exactly what the warning text already tells them to do.

Two secondary hardening suggestions:

- **Include the attempt count in the recursion budget.** Even with the fix above, any future
  path that leaves `not current` true with `may_retry` true can nest. A depth counter in the
  relaunch command (e.g. via an env var consumed by `prepare_launch`) would make the loop
  structurally impossible.
- **Make the two "changed while preparing publication" guards distinguishable.** A separate
  observation from this install: `pm/install.py:722` raised
  `ValueError("Dependency inputs changed while preparing publication; retry.")` on one run
  and then succeeded on an identical immediate re-run, with the repo `uv.lock`
  (`mtime 2026-09-30 01:01:20 UTC`), `pm/lock.json` (`mtime 2026-09-28`), the store target,
  and all 14 enabled plugin members verified byte-identical across a 75 s window. The guard
  is intermittent here and its trigger could not be reproduced; worth a look, but reported
  only as an observation, not a confirmed defect.

## 5. Reproduction

```powershell
# 1. land a source update that changes the dependency contract, with the tail failing
#    until installs\<key>\source-completion-attempts reaches 6
# 2. confirm the precondition without triggering the loop (read-only):
python -c "import sys; sys.path.insert(0, r'<install>\hermes-agent'); `"
          "from hermes_cli.venv_sync import main; `"
          "sys.exit(main(['--project-root', r'<install>\hermes-agent', '--check', '--json']))"
#    -> {"state": "would-sync", "ok": true}      (i.e. not current)
# 3. run any non-metadata command, e.g. `hermes checkpoints status`
#    -> hangs; warning repeats per level; Ctrl+C unwinds one level at a time
```

## 6. Workaround

Reset the retry record and let the repair run again — it is plain per-install state beside
the pending marker:

```
installs\<key>\source-completion-attempts   # set to 0, or delete
```

With the counter reset, `completion_retry_state()` returns `(True, 0, 0)`, the repair branch
is reachable again, and a successful sync makes `venv_is_current` true — which removes the
`not current` term from the relaunch condition and ends the recursion.

---

*Filed from an OPTIMUS Prime swarm node. Environment, paths and evidence quoted verbatim from
the affected machine.*

