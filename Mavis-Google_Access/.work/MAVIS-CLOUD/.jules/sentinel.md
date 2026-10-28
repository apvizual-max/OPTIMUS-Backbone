## 2026-10-23 - Command injection vulnerabilities in python subprocess.run
**Vulnerability:** Python `subprocess.run` calls were executed with `shell=True`, which is vulnerable to command injection if variables substituted in commands are not properly escaped.
**Learning:** Shell=True enables execution of arbitary shell commands if user input reaches the command string.
**Prevention:** Use a list with `shell=False` for executing commands securely, as specified in memory guidelines. Avoid `shell=True` unless absolutely necessary (and if used, heavily sanitize).

## 2026-10-23 - XSS vulnerability via innerHTML in SITE/build-hub.py
**Vulnerability:** User-controlled input was inserted unsanitized into `.innerHTML`, leading to a Cross-Site Scripting (XSS) vulnerability.
**Learning:** Using `.innerHTML` to insert text without proper HTML escaping allows for the execution of arbitrary JavaScript. Also, when embedding JS containing curly braces within Python string templates, they must be escaped (`{{`, `}}`) to avoid Python formatting errors.
**Prevention:** Always use a helper function to HTML-escape variables when concatenating strings to be injected into `.innerHTML`, or avoid using `.innerHTML` altogether and prefer methods that treat input strictly as text (e.g. `textContent`).

## 2026-10-25 - Command injection vulnerabilities via shell=True in mavis-tools/sentinel.py
**Vulnerability:** Python `subprocess.run` calls were executing with `shell=True` using string arguments, leading to command injection vulnerabilities.
**Learning:** `shlex.split()` combined with string commands for `subprocess.run` breaks when the string contains shell-specific syntax like `2>/dev/null`, and the `shell=True` risk remains if user inputs aren't escaped securely.
**Prevention:** Pass command arguments directly as lists and set `shell=False` in `subprocess.run()`. Handle IO stream redirection natively using `capture_output=True` (or passing `subprocess.DEVNULL` to `stderr`) instead of relying on shell operators. Unit tests for these calls should assert against the list arguments properly.

## 2026-10-26 - Command injection vulnerabilities via shell=True in SITE/build-dashboard-legacy.py
**Vulnerability:** Python `subprocess.run` calls were executing with `shlex.split` parsing string commands, which still opens up risks if underlying implementation or caller assumptions change, or if a user refactors it back to `shell=True`. Furthermore, unit tests were mocked against string lists but failed when `shell=False` was explicitly added.
**Learning:** Always explicitly set `shell=False` and pass list arguments natively, bypassing `shlex.split` entirely when possible. Ensure test assertions (`mock_run.assert_called_once_with`) explicitly verify `shell=False` and match the exact invocation signature.
**Prevention:** Pass command arguments directly as lists and set `shell=False` in `subprocess.run()`. Update any mocks in unit tests to assert `shell=False`.
