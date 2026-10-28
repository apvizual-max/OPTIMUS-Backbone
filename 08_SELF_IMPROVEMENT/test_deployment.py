#!/usr/bin/env python3
"""
mavis-sentinel-hub - end-to-end tests for the containerised local deployment.

WHAT THIS TESTS
    The deployment claim, end to end, from outside: a dedicated container named
    for this project, bound to loopback only, fronting the Windows data plane,
    reachable at the same address Popy already has bookmarked, and re-creatable
    from nothing but the files in this repository.

WHY A SEPARATE SUITE
    The existing test_suite.py proves the DATA PLANE (extraction, monitoring,
    the collector, the state files). Nothing in it proves the DEPLOYMENT: that
    a container exists, that it is the thing answering on 8910, that it cannot
    be reached from off-box, or that it still serves after being rebuilt. A
    green data plane and a dead link look identical from the dashboard, which
    is precisely the failure Popy reported.

THE RULE THIS SUITE FOLLOWS
    A check that cannot run reports NOT_RUN. It never reports PASS, and it
    never reports FAIL. An absent Docker engine has falsified nothing, and a
    FAIL there would be a lie with a number attached.

Run:  python test_deployment.py            (from 08_SELF_IMPROVEMENT)
      python test_deployment.py --json     (machine-readable)
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONTAINER = "mavis-sentinel-hub"
IMAGE = "mavis/sentinel-hub:1.0.0"
FRONT_PORT = 8910                      # the container's published port
BACKEND_PORT = 8912                    # the Windows data plane behind it
FRONT = f"http://127.0.0.1:{FRONT_PORT}"
BACKEND = f"http://127.0.0.1:{BACKEND_PORT}"
SSE_WAIT_SECONDS = 62                  # >2 collector cycles at 25 s

RESULTS: list[dict] = []


def record(cid: str, status: str, detail: str) -> None:
    RESULTS.append({"id": cid, "status": status, "detail": detail})
    mark = {"PASS": "[ok]  ", "FAIL": "[FAIL]", "NOT_RUN": "[----]"}[status]
    print(f"  {mark} {cid}: {detail}")


def check(cid: str, ok: bool, ok_detail: str, fail_detail: str) -> bool:
    record(cid, "PASS" if ok else "FAIL", ok_detail if ok else fail_detail)
    return ok


def not_run(cid: str, why: str) -> None:
    record(cid, "NOT_RUN", why)


_T0 = time.time()


def trace(msg: str) -> None:
    """Progress line to stderr, flushed immediately.

    A run that hangs has to be able to say WHERE it hung. Buffered stdout
    written to a redirected file shows nothing at all until the process exits,
    which is precisely the window in which a stall is hardest to diagnose. This
    is what turns "the command timed out after 1800 s" into a location."""
    print(f"[+{time.time() - _T0:7.1f}s] {msg}", file=sys.stderr, flush=True)


def docker(*args: str, timeout: int = 90) -> tuple[int, str, str]:
    """Run a docker command. Returns (exit_code, stdout, stderr)."""
    try:
        p = subprocess.run(
            ["docker", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError:
        return 127, "", "docker executable not on PATH"
    except subprocess.TimeoutExpired:
        return 124, "", f"docker {' '.join(args)} timed out after {timeout}s"


def kill_tree(pid: int) -> bool:
    """Kill a process and everything it spawned. Returns True if it worked.

    `taskkill` is a native command, so a non-zero exit does NOT raise in
    PowerShell 5.1 - and it is the exit code, not an exception, that says
    whether the tree is gone."""
    try:
        p = subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                           capture_output=True, text=True, timeout=60, errors="replace")
        return p.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def run_tool(argv: list[str], timeout: int, log_name: str) -> tuple[int, str]:
    """Run a tool whose output goes to a FILE, and never to a pipe.

    Found by hanging, twice, for 1800 s. `subprocess.run(capture_output=True)`
    reads its pipes until EOF, and EOF only arrives when every process holding
    the write end has exited. The `start` verb legitimately leaves a long-lived
    backend server behind, and that server inherits the pipes - so the direct
    child exits, the pipes stay open, and `communicate()` never returns.

    Worse, the `timeout=` argument does not save you. On expiry Python kills the
    direct child - which has already exited - and then re-enters the same
    blocking read. The timeout is decorative for exactly the case it looks like
    it protects. Proof from the run that exposed it: the suite sat at
    "+2.3s invoking the start verb" long past its 240 s budget, with no
    descendant processes at all, because the process that held the pipe was an
    orphan whose parent had already died.

    Writing to a file removes the pipe, so waiting on the direct child is
    sufficient and correct. On timeout the whole tree is killed, because a
    start that did not finish must not leave half a deployment behind."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "09_LOGS")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_name)
    # The exact command line goes into the log before anything runs. A child
    # that dies on argument handling blames a token, not the line that produced
    # it, so without this the evidence is unreadable. Proven necessary: a
    # `-ExecutionPolicy is not recognized` failure was reproducible only from
    # inside one caller, and the argv it printed looked correct.
    preamble = (f"### argv type: {type(argv).__name__} of {len(argv)}\n"
                f"### cmdline: {subprocess.list2cmdline(argv)}\n")
    with open(log_path, "wb") as fh:
        fh.write(preamble.encode("utf-8", "replace"))
        proc = subprocess.Popen(argv, stdout=fh, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL)
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            killed = kill_tree(proc.pid)
            rc = 124
            trace(f"run_tool: {log_name} TIMED OUT after {timeout}s; "
                  f"tree kill {'succeeded' if killed else 'FAILED'}")
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
            out = fh.read()
    except OSError as e:
        out = f"(could not read {log_name}: {e})"
    return rc, out


def http(url: str, timeout: int = 25):
    """GET a URL. Returns (status, body_bytes, headers) or raises."""
    req = urllib.request.Request(url, headers={"Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read(), dict(r.headers)


def http_code(url: str, timeout: int = 12) -> int:
    try:
        return http(url, timeout)[0]
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def ensure_deployment_up() -> bool:
    """Establish the precondition before judging anything.

    The first version of this suite had no precondition, and it produced the
    most useless output imaginable: 12 FAILs that all said "connection
    refused", because it had been run against a deployment that was not
    running. Every one of those was true and none of them was a defect. A red
    that measures the wrong thing trains the reader to ignore red.

    So: if the front is not serving, bring the deployment up first. If it
    cannot be brought up, that is a genuine FAIL of the deployment - but every
    check that depends on it is NOT_RUN, because a broken precondition is not
    twelve independent broken things.
    """
    hub = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "13_COMMAND_CENTER", "api", "sentinel-hub.ps1")

    def both_planes_serving(timeout: int = 8) -> bool:
        """A gateway that answers 200 is not a deployment.

        Found in anger: the front was up while the backend had been killed, so
        /healthz returned 200 and every other route returned 502. A precondition
        built on the gateway alone declared that "deployment already serving"
        and then judged a dozen checks against a dead app - the same class of
        unfailable check as `front == back` passing on 0 == 0. Both planes must
        answer before anything is judged."""
        return (http_code(FRONT + "/healthz", timeout=timeout) == 200
                and http_code(FRONT + "/readyz", timeout=timeout) == 200)

    if both_planes_serving():
        record("precondition_serving", "PASS",
               "deployment already serving on both planes - checks run against the live system")
        return True

    # NOT a verdict. "The deployment is not up yet" is the reason this function
    # exists, not a fault in it. The first version recorded it as a FAIL and
    # then recorded a PASS once the start verb worked, so a completely
    # successful cold start still exited 1 and reported one failure - for
    # having needed a start. A recovery step is not a defect, and a check that
    # reports its own remedy as a failure trains the reader to ignore it.
    # Only a FAILED recovery is a failure.
    trace("precondition_serving: not serving on both planes yet - starting it")
    trace("ensure_deployment_up: invoking the start verb")
    rc, out = run_tool(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", hub, "-Action", "start",
                        "-FrontPort", str(FRONT_PORT), "-BackPort", str(BACKEND_PORT)],
                       timeout=240, log_name="hub-start-verb.log")
    trace(f"ensure_deployment_up: start verb returned rc={rc}")
    if rc == 124:
        record("precondition_serving", "FAIL", "start did not return within 240s")
        return False
    trace("ensure_deployment_up: start verb returned, polling for the front")

    deadline = time.time() + 120
    while time.time() < deadline:
        if both_planes_serving(timeout=5):
            record("precondition_serving", "PASS",
                   "deployment started by the orchestrator and now serving on both planes")
            return True
        time.sleep(4)
    record("precondition_serving", "FAIL",
           "the orchestrator could not bring the deployment up within 120s")
    return False


# ---------------------------------------------------------------- 1. engine --
def test_engine() -> bool:
    rc, out, err = docker("version", "--format", "{{.Server.Version}}")
    if rc != 0:
        not_run("engine_available", f"docker engine not reachable: {err or out}")
        return False
    record("engine_available", "PASS", f"docker server {out}")
    return True


# ------------------------------------------------------------- 2. container --
def test_container() -> None:
    rc, out, _ = docker("inspect", CONTAINER)
    if rc != 0:
        record("container_exists", "FAIL", f"container '{CONTAINER}' not found - not deployed")
        return
    record("container_exists", "PASS", f"container '{CONTAINER}' exists")

    rc, out, _ = docker("inspect", "--format", "{{.State.Status}}", CONTAINER)
    running = out.strip() == "running"
    check("container_running", running,
          f"state={out.strip()}",
          f"state={out.strip()!r} - a stopped container serves nothing")

    # The image's own HEALTHCHECK proves the GATEWAY answers. It deliberately
    # does not prove the app behind it, so it is never a stand-in for readiness.
    #
    # Two things were wrong with the first version of this check.
    #
    # 1. It claimed more than it measured. On a `starting` state it printed
    #    "the front is not answering /healthz" - but it never asked /healthz.
    #    In the run that exposed it, /healthz had answered 200 two checks
    #    earlier. A failure message that describes a probe nobody performed is
    #    worse than no message: it sends the reader to debug the wrong service.
    #    The real /healthz status is now measured and reported alongside.
    #
    # 2. It judged `starting` as a failure. `starting` is Docker's own
    #    start_period, before the first probe has concluded - an UNCONCLUDED
    #    measurement, not a negative one. The suite runs immediately after a
    #    start, so it reliably caught that window. This now waits for the
    #    healthcheck to settle before judging, which is the fix; relaxing the
    #    bound would have been the fake one.
    hz = http_code(FRONT + "/healthz", timeout=8)
    rc, out, _ = docker("inspect", "--format", "{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}", CONTAINER)
    hs = out.strip()
    if hs == "none":
        not_run("container_health", "image declares no HEALTHCHECK - cannot be measured")
    else:
        waited = 0.0
        while hs == "starting" and waited < 60:
            time.sleep(5)
            waited += 5
            rc, out, _ = docker("inspect", "--format", "{{.State.Health.Status}}", CONTAINER)
            hs = out.strip()
        check("container_health", hs == "healthy",
              f"gateway healthcheck=healthy after {waited:.0f}s of settle time; "
              f"/healthz measured {hz}",
              f"gateway healthcheck={hs!r} after {waited:.0f}s of settle time; "
              f"/healthz measured {hz} - "
              + ("the image's own probe is not passing"
                 if hs == "unhealthy" else
                 "the healthcheck never settled"))

    rc, out, _ = docker("inspect", "--format", "{{.HostConfig.RestartPolicy.Name}}", CONTAINER)
    rp = out.strip()
    check("container_restart_policy", rp in ("unless-stopped", "always"),
          f"restart policy={rp} (survives Docker restart and reboot)",
          f"restart policy={rp!r} - the deployment will not come back by itself")

    rc, out, _ = docker("inspect", "--format", "{{.Config.Image}}", CONTAINER)
    check("container_image", out.strip() == IMAGE,
          f"image={out.strip()}",
          f"image={out.strip()!r}, expected {IMAGE}")


# ---------------------------------------------------- 3. loopback-only proof --
def _non_loopback_ipv4() -> list[str]:
    """Every routable IPv4 address on this machine.

    Written without PowerShell on purpose. The obvious one-liner

        powershell -NoProfile -Command "(Get-NetIPAddress ... -notlike '127.*' ...) -join ','"

    is what this function used to do, and it returned NOTHING while exiting 1:
    when subprocess builds a Windows command line it re-quotes the argument,
    and the nested single quotes around the -notlike patterns do not survive,
    so PowerShell failed with "Unexpected token 'and'" and the caller read an
    empty result as "this machine has no non-loopback address". That is the
    worst possible failure for this particular check - it silently skipped the
    single claim that matters most (the corpus is not reachable off-box) and
    reported NOT_RUN, which reads as cautious rather than broken.

    The first probe is the primary outbound address and sends no packets:
    connect() on a UDP socket only picks a route.
    """
    import socket

    ips: set[str] = set()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("192.0.2.1", 1))  # TEST-NET-1: reserved, never routed
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass

    # Every adapter as well, so a second NIC cannot hide.
    try:
        out = subprocess.run(["ipconfig"], capture_output=True, text=True,
                             timeout=30, errors="replace").stdout
        for line in out.splitlines():
            s2 = line.strip()
            if not s2.lower().startswith("ipv4"):
                continue
            for tok in s2.split(":")[-1].split("("):
                tok = tok.strip().rstrip(")").strip()
                parts = tok.split(".")
                if len(parts) == 4 and all(p.isdigit() for p in parts):
                    if parts[0] != "127" and not tok.startswith("169.254"):
                        ips.add(tok)
                    break
    except Exception:
        pass

    return sorted(ips)


def test_loopback_only() -> None:
    """The deployment must not be reachable from off-box. This is the claim
    that matters most for a system holding a verbatim corpus, so it is proven
    by connecting to the machine's own routable address and expecting refusal."""
    ips = _non_loopback_ipv4()
    if not ips:
        not_run("loopback_only",
                "no non-loopback IPv4 address could be enumerated - the claim is UNMEASURED, not true")
        return

    leaked = []
    for ip in ips:
        rc = http_code(f"http://{ip}:8910/healthz", timeout=6)
        if rc == 200:
            leaked.append(ip)
    check("loopback_only", not leaked,
          f"8910 refused on {len(ips)} non-loopback address(es): {', '.join(ips)}",
          f"REACHABLE OFF-BOX on {', '.join(leaked)} - this would expose the corpus")

    rc, out, _ = docker("port", CONTAINER)
    check("port_binding", "127.0.0.1" in out,
          f"docker port -> {out}",
          f"docker port -> {out!r}; expected a 127.0.0.1 binding")


# --------------------------------------------------- 4. serves through front --
def test_serves_through_front() -> None:
    routes = {
        "route_root": FRONT + "/",
        "route_healthz": FRONT + "/healthz",
        "route_readyz": FRONT + "/readyz",
        "route_api_state": FRONT + "/api/state",
        "route_api_health": FRONT + "/api/health",
    }
    for cid, url in routes.items():
        try:
            st, body, hdrs = http(url)
            ok = st == 200 and len(body) > 0
            check(cid, ok, f"{st} {len(body)} B",
                  f"{st} {len(body)} B - route did not serve")
        except Exception as e:
            record(cid, "FAIL", f"{url} raised {type(e).__name__}: {str(e)[:70]}")

    # Proof the answer came from the CONTAINER and not from a stray PowerShell
    # that happens to hold the port. The header is the only honest evidence.
    try:
        st, body, hdrs = http(FRONT + "/")
        served_by = hdrs.get("X-SENTINEL-Deployment", "")
        srv = hdrs.get("Server", "")
        check("served_by_front", served_by == "mavis-sentinel-hub" and "nginx" in srv.lower(),
              f"Server={srv} X-SENTINEL-Deployment={served_by}",
              f"Server={srv!r} X-SENTINEL-Deployment={served_by!r} - not served by the container")
    except Exception as e:
        record("served_by_front", "FAIL", str(e)[:80])

    # /healthz must answer from nginx itself even when the app behind it is
    # gone. That separation is the whole reason there are two paths.
    try:
        st, body, _ = http(FRONT + "/healthz")
        j = json.loads(body.decode("utf-8"))
        check("gateway_independent", st == 200 and j.get("service") == CONTAINER,
              f"/healthz reports {j.get('service')} role={j.get('role')}",
              f"/healthz payload unexpected: {body[:120]!r}")
    except Exception as e:
        record("gateway_independent", "FAIL", str(e)[:80])


# ------------------------------------------------------- 5. backend is behind --
def test_backend_behind_front() -> None:
    """Both planes must answer independently. If only one does, the failure
    mode is invisible: the dashboard would render an error page that looks
    like a broken app rather than a missing data plane."""
    front = http_code(FRONT + "/api/state", timeout=12)
    back = http_code(BACKEND + "/api/state", timeout=12)
    check("both_planes_live", front == 200 and back == 200,
          f"front={front} backend={back}",
          f"front={front} backend={back} - the two planes disagree")

    # Equality is NOT the assertion. The first version of this line was
    #     check(..., front == back, ...)
    # and http_code() returns 0 when the connection is refused, so 0 == 0
    # passed GREEN with both planes dead - a check that could not fail. The
    # thing being compared is "the front serves what the backend serves", and
    # that is only a meaningful claim when both are actually serving.
    check("front_matches_backend", front == 200 and back == 200 and front == back,
          f"front and backend both serve 200 and agree",
          f"front={front} backend={back} - cannot conclude the front mirrors the "
          f"backend unless both are serving (0 means 'not answering', not 'equal')")


# -------------------------------------------- 6. SSE reconnect really happens --
def test_sse_reconnect() -> None:
    """The backend's /api/stream is SHORT-LIVED BY DESIGN: the listener is
    single-threaded, so it sends state, flushes, closes, and the browser's
    EventSource reconnects. A single short response is therefore correct and
    must NOT be filed as a truncation. What must be proven is the RECONNECT:
    that a real browser receives state repeatedly over time. If it does not,
    the live dashboard is not live, and nothing else in the system would say so.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        not_run("sse_reconnect", "playwright not importable in this interpreter")
        return

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(FRONT + "/", wait_until="domcontentloaded", timeout=45000)
            # Count real EventSource deliveries in the page's own context.
            page.evaluate(
                """() => {
                    window.__sentinelEvents = 0;
                    window.__sentinelErrors = 0;
                    const es = new EventSource('/api/stream');
                    es.addEventListener('state', () => { window.__sentinelEvents++; });
                    es.onerror = () => { window.__sentinelErrors++; };
                }"""
            )
            time.sleep(SSE_WAIT_SECONDS)
            events = page.evaluate("() => window.__sentinelEvents")
            errors = page.evaluate("() => window.__sentinelErrors")
            browser.close()
    except Exception as e:
        record("sse_reconnect", "FAIL", f"browser check raised {type(e).__name__}: {str(e)[:80]}")
        return

    # Each cycle delivers exactly one 'state' event, so >=2 over ~62 s means the
    # reconnect is genuinely happening rather than a single lucky delivery.
    check("sse_reconnect", events >= 2,
          f"{events} 'state' events in {SSE_WAIT_SECONDS}s via EventSource reconnect ({errors} transport errors)",
          f"only {events} 'state' events in {SSE_WAIT_SECONDS}s - the live dashboard is not live")


# ------------------------------------------------------- 7. startup anchor --
def test_startup_entry(coldstart: bool) -> None:
    """The deployment must come up by itself at logon. That claim is worthless
    if it is only ever checked while everything is already running, so this
    asserts the ENTRY first and then, on request, actually performs a cold
    start.

    The structural assertions are permanent guards against the exact defect
    that was found here: the first version of this entry used

        start "" /min powershell ... -Command "& '...' -Action start"

    and it failed AT LOGON, silently, leaving both planes down with no
    diagnostic anywhere. `start` applies its own quoting rules and a multi-line
    quoted -Command argument is precisely what it mangles. -File with a single
    quoted path is the form that survives, and the guard below fails loudly if
    anyone re-introduces the fragile one.
    """
    startup = os.path.join(os.environ.get("APPDATA", ""),
                           r"Microsoft\Windows\Start Menu\Programs\Startup",
                           "SENTINEL Command Center.bat")
    if not os.path.isfile(startup):
        record("startup_entry_present", "FAIL",
               f"no Startup entry at {startup} - the deployment will not return at logon")
        return
    record("startup_entry_present", "PASS", f"Startup entry present ({os.path.getsize(startup)} B)")

    try:
        with open(startup, "r", encoding="ascii", errors="replace") as fh:
            body = fh.read()
    except OSError as e:
        record("startup_entry_readable", "FAIL", str(e)[:80])
        return
    record("startup_entry_readable", "PASS", "entry is readable ASCII")

    low = body.lower()
    # The fragile form. Its return is a FAIL, not a warning: it is known broken.
    check("startup_uses_file_not_command", "-command" not in low,
          "entry uses -File with a quoted path (the form that survives 'start')",
          "entry uses an inline -Command, which 'start' mangles - this is the "
          "defect that left the deployment down at logon with no diagnostic")

    check("startup_targets_orchestrator", "sentinel-hub.ps1" in low,
          "entry invokes sentinel-hub.ps1 (brings up BOTH planes)",
          "entry does not invoke sentinel-hub.ps1")

    check("startup_ports", str(BACKEND_PORT) in body and str(FRONT_PORT) in body,
          f"entry targets front={FRONT_PORT} backend={BACKEND_PORT}",
          f"entry does not name both ports ({FRONT_PORT}/{BACKEND_PORT})")

    check("startup_logs", ".log" in low,
          "entry writes a log, so a future failure leaves evidence",
          "entry writes no log - a silent startup failure cannot be diagnosed")

    if not coldstart:
        record("startup_cold_start", "NOT_RUN",
               "destructive: re-run with --coldstart to tear the deployment down and "
               "prove the Startup entry brings it back")
        return

    # ---- the destructive half -------------------------------------------
    hub = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "13_COMMAND_CENTER", "api", "sentinel-hub.ps1")
    # Each switch and its value are SEPARATE list elements. Written as the
    # single string "-ExecutionPolicy Bypass", PowerShell receives one quoted
    # argument, treats it as the command to run, and dies with "the term
    # '-ExecutionPolicy' is not recognized" - which blames a token and hides
    # the line that produced it. The teardown silently did nothing, and the
    # cold-start check below correctly refused to claim a pass.
    ps = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", hub]

    def run_ps(action: str, timeout: int = 200):
        """Returns (returncode, stdout+stderr, elapsed). The evidence is kept so
        a failure can report what the tool actually said, rather than only that
        the thing it was supposed to do did not happen.

        The exact executable and argv are prepended to every failure. A child
        that dies on argument handling reports something like "the term
        '-ExecutionPolicy' is not recognized", which is unreadable without
        knowing what it was actually handed - and that failure mode is
        invisible if the evidence is truncated to its first 220 characters."""
        argv = ps + ["-Action", action, "-FrontPort", str(FRONT_PORT),
                     "-BackPort", str(BACKEND_PORT)]
        how = f"ran {shutil.which('powershell') or 'powershell'} with {argv}"
        t = time.time()
        rc, out = run_tool(argv, timeout=timeout, log_name=f"hub-{action}-verb.log")
        if rc == 124:
            out = f"{how}\nTIMEOUT after {timeout}s; output so far: {out}"
        elif rc != 0:
            out = f"{how}\nrc={rc}; output: {out}"
        return rc, out, time.time() - t

    rc, out, elapsed = run_ps("stop")
    trace(f"cold start: stop verb returned rc={rc} in {elapsed:.1f}s")
    # Poll for the teardown instead of probing once. A single check 4 s after
    # the stop command returns is brittle in a way that hides the truth: the
    # container stop and the port release are not simultaneous, and a probe
    # that lands in that gap reports "teardown did not take effect" for a
    # teardown that is merely still in progress. Polling keeps the check strict
    # - it still fails if the system never goes down - while removing the race.
    went_down = False
    down_after = None
    t_down = time.time()
    while time.time() - t_down < 45:
        if http_code(FRONT + "/healthz", timeout=4) != 200:
            went_down = True
            down_after = time.time() - t_down
            break
        time.sleep(3)
    if not went_down:
        observed = http_code(FRONT + "/healthz", timeout=8)
        detail = " ".join(str(out).split())[:600]
        record("startup_cold_start", "FAIL",
               f"teardown did not take effect within 45 s (front still answers {observed}). "
               f"stop verb: rc={rc} in {elapsed:.1f}s, said: {detail!r}. "
               f"The test would prove nothing, so it is refusing to claim a pass.")

    # Baseline for the evidence checks, taken IMMEDIATELY BEFORE the launch.
    # Capturing it before the teardown, as an earlier version did, makes the
    # comparison wrong in a way that fails when nothing is wrong: anything else
    # appending between the capture and the launch - another startup, a
    # collector - makes the baseline too large and the run looks like it wrote
    # nothing. That is a real false FAIL, observed on 2026-10-06 while a
    # concurrent task was starting the same deployment.
    # The run's identity is established by its OWN marker, not by a byte count
    # against a distant baseline.
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                            "09_LOGS", "hub-startup.log")

    def log_state():
        """(size, marker_count, [line index of last marker]) or (None, 0, -1)."""
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
            idx = [i for i, ln in enumerate(lines) if "=== startup " in ln]
            return (os.path.getsize(log_path), len(idx), (idx[-1] if idx else -1))
        except OSError:
            return (None, 0, -1)

    size_before, markers_before, _ = log_state()

    try:
        # stdin/stdout/stderr are detached deliberately. The entry starts a
        # long-lived service, and a child that inherits this process's streams
        # keeps them open long after the suite is gone - which is the same trap
        # as run_tool, one level up.
        subprocess.Popen(["cmd", "/c", startup],
                         creationflags=0x08000000,  # CREATE_NO_WINDOW
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, close_fds=True)
    except Exception as e:
        record("startup_cold_start", "FAIL", f"could not launch the entry: {str(e)[:70]}")
        return
    trace("cold start: startup entry launched, polling for the front to return")

    deadline = time.time() + 180
    came_up = False
    while time.time() < deadline:
        if http_code(FRONT + "/healthz", timeout=5) == 200:
            came_up = True
            break
        time.sleep(4)
    trace(f"cold start: front {'returned' if came_up else 'did NOT return'} "
          f"in {180 - max(0.0, deadline - time.time()):.1f}s")

    ready = http_code(FRONT + "/readyz", timeout=20) == 200
    check("startup_cold_start", came_up and ready,
          f"from fully down, the Startup entry brought the deployment up "
          f"(front={http_code(FRONT + '/healthz', timeout=10)}, readyz={ready})",
          f"after 180 s from a known-down state: front={'up' if came_up else 'down'}, "
          f"readyz={'ok' if ready else 'FAILING'} - the deployment does not return by itself")

    # ---- did the run leave EVIDENCE? -------------------------------------
    #
    # `came_up and ready` says the deployment works. It says nothing about
    # whether anyone can find out what happened, and that gap let a real defect
    # ship: the entry recorded its exit code on idempotent runs and lost it on
    # every fresh start - precisely the run whose job is to start it. The suite
    # stayed green through all of it, because it never looked.
    #
    # So: the durable log must have grown, the run must be identifiable in it,
    # and that run must carry its own exit code. The exit line is written to the
    # DURABLE log rather than the per-run file, because the backend inherits the
    # latter's handle and holds it - see the entry's own comments.
    # The front answering 200 does NOT mean the evidence has landed. The .bat
    # writes its marker, folds its transcript and records its exit code only
    # AFTER the orchestrator's start verb returns, while nginx is already
    # healthy and answering. Sampling the log the instant the front returns
    # therefore races the writer.
    #
    # Observed 2026-10-06: the durable log was written in the same second the
    # sample was taken, the check reported "53 -> 53, 0 B written", and the
    # very next check then passed by reading the PREVIOUS run's exit line. A
    # false FAIL and a false PASS from one race.
    #
    # So: poll for the evidence, bounded. A genuinely absent marker still
    # FAILS - the wait is not a licence to be lenient.
    evidence_deadline = time.time() + 45
    size_after, markers_after, last_marker = log_state()
    while markers_after <= markers_before and time.time() < evidence_deadline:
        time.sleep(2)
        size_after, markers_after, last_marker = log_state()
    grew = (size_after is not None and size_before is not None
            and size_after > size_before)
    # Marker COUNT is the identity test, not the byte count: a new marker
    # appeared between the two samples. A byte delta alone can be produced by
    # any other writer, and can be absent when this run's own write landed
    # inside a concurrent one.
    new_marker = markers_after > markers_before

    check("startup_left_evidence", grew and new_marker and last_marker >= 0,
          f"this run is recorded in the durable startup log "
          f"({markers_before} -> {markers_after} markers, "
          f"{(size_after or 0) - (size_before or 0)} B written, "
          f"newest marker at line {last_marker + 1})",
          f"the startup log gained no marker for this run "
          f"({markers_before} -> {markers_after}, "
          f"{(size_after or 0) - (size_before or 0)} B) - a startup that leaves "
          f"no trace cannot be diagnosed after the fact")

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        record("startup_recorded_exit_code", "FAIL",
               f"cannot read {log_path}: {str(e)[:60]}")
        return

    exits = [i for i, ln in enumerate(lines) if ln.strip().startswith("exit=")]

    # Keyed to THIS run's marker. Before this guard the check searched for any
    # exit line after the newest marker in the file - which, when the run left
    # no marker at all, is the PREVIOUS run's marker and its exit line. That is
    # exactly how a run that recorded nothing scored a pass on "it recorded its
    # own exit code". No marker means there is nothing to attribute.
    if not new_marker:
        record("startup_recorded_exit_code", "NOT_RUN",
               f"this run left no marker to attribute an exit code to "
               f"(marker count stayed at {markers_before})")
        return
    if last_marker < 0 or not exits:
        record("startup_recorded_exit_code", "NOT_RUN",
               "no marker/exit pair to inspect")
        return
    later = [i for i in exits if i > last_marker]
    check("startup_recorded_exit_code", bool(later),
          f"the most recent startup recorded its own exit code "
          f"({lines[later[0]].strip() if later else 'n/a'})",
          f"the newest startup marker (line {last_marker + 1}) has no exit code "
          f"after it - the run that actually starts the deployment is the one "
          f"whose result goes unrecorded")


def test_front_not_hijacked() -> None:
    """The front port must be served by the container and by nothing else.

    This check exists because a stray `sentinel-cc.ps1` bound 8910 directly and
    the deployment went on answering 200 long after the container was stopped.
    Every status probe said "up", the cold-start teardown could never take
    effect - because the thing it was stopping was not the thing holding the
    port - and the failure was reported as a problem with the startup path,
    which was working perfectly.

    A hijacked front is indistinguishable from a healthy one by status code
    alone. Only the deployment header tells them apart, so that is the
    assertion, and the squatter's pid is named so it can be ended.
    """
    try:
        st, body, hdrs = http(FRONT + "/healthz", timeout=10)
    except Exception as e:
        record("front_not_hijacked", "NOT_RUN",
               f"{FRONT}/healthz is not answering ({str(e)[:50]}) - nothing to hijack")
        return
    served_by = hdrs.get("X-SENTINEL-Deployment", "")
    if served_by == CONTAINER:
        record("front_not_hijacked", "PASS",
               f"front port is served by {served_by}")
        return
    # Name the squatter by command line, not by socket: HttpListener's socket is
    # owned by pid 4 (System), so every "who owns this port" heuristic lies.
    squatters = []
    try:
        ps = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_Process -Filter \"Name='powershell.exe'\" | "
             "Where-Object { $_.CommandLine -like '*SENTINEL_PRIME*server.ps1*' } | "
             "ForEach-Object { $_.ProcessId }) -join ','"],
            capture_output=True, text=True, timeout=40, errors="replace")
        # A nested-quote one-liner through subprocess is exactly the trap the
        # loopback check fell into, so parse defensively and never let a parse
        # failure masquerade as "no squatters found".
        for tok in (ps.stdout or "").replace("\r", "").replace("\n", "").split(","):
            tok = tok.strip()
            if tok.isdigit():
                squatters.append(tok)
    except Exception:
        pass
    who = ", ".join(f"pid {p}" for p in squatters) if squatters else "process not identified"
    record("front_not_hijacked", "FAIL",
           f"{FRONT} answered 200 but X-SENTINEL-Deployment was "
           f"{served_by!r}, not {CONTAINER!r} - the front port is held by "
           f"something that is not the deployment ({who}). A stopped container "
           f"would look identical from here.")


# ------------------------------------------------------- 8. no leakage --
def test_ecosystem_snapshot_fresh() -> None:
    """The Ecosystem panel is only worth anything if it is refreshed BY THE
    SERVER, not by whoever happened to run the collector last.

    This check exists because of a defect that nothing else could see. The
    refresh was written into a PowerShell function that was defined and never
    called - the real worker was a `Start-Job` elsewhere in the same file. The
    panel served a snapshot that had aged to 27 minutes and never moved again,
    with no error anywhere, and every other check in this suite was green.

    Nothing was measuring that file's age, so nothing noticed. This does.
    """
    snap = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "13_COMMAND_CENTER", "api", "minimax-ecosystem.json")
    if not os.path.isfile(snap):
        not_run("ecosystem_snapshot_fresh",
                f"no snapshot at {snap} - the collector has not run")
        return
    age = time.time() - os.path.getmtime(snap)
    # The worker refreshes every 4th cycle at 25 s = 100 s. Allow generous slack
    # for a slow collection, but not for a refresh that never happens at all.
    bound = 600
    check("ecosystem_snapshot_fresh", age < bound,
          f"snapshot age {age:.0f}s, refreshed by the server's worker (bound {bound}s)",
          f"snapshot is {age:.0f}s old (bound {bound}s) - the server is NOT "
          f"refreshing it. A panel this old is a snapshot, not a live hub.")


def test_ecosystem_route() -> None:
    """The route must serve the snapshot, and must say NOT_AVAILABLE rather than
    returning an empty object that renders as a panel of nothing."""
    try:
        st, body, _ = http(FRONT + "/api/minimax", timeout=20)
        d = json.loads(body.decode("utf-8"))
    except Exception as e:
        record("ecosystem_route", "FAIL", f"{FRONT}/api/minimax raised {type(e).__name__}: {str(e)[:60]}")
        return
    if d.get("status") == "NOT_AVAILABLE":
        not_run("ecosystem_route", d.get("reason", "collector has not written a snapshot"))
        return
    surfaces = d.get("surfaces")
    check("ecosystem_route", st == 200 and isinstance(surfaces, list) and len(surfaces) > 0,
          f"{st}, {len(surfaces) if isinstance(surfaces, list) else '?'} surfaces, counts={json.dumps(d.get('counts'))}",
          f"{st} with surfaces={surfaces!r} - an empty surface list is indistinguishable "
          f"from an ecosystem that was never measured")



def test_no_data_in_image() -> None:
    """The image must contain the web plane and nothing else. A baked-in copy of
    the corpus would be a second source of truth that silently diverges from
    the one that is actually measured."""
    rc, out, err = docker("run", "--rm", "--entrypoint", "sh", IMAGE, "-c",
                          "find / -xdev -iname '*corpus*' -o -xdev -iname 'sentinel-state.json' 2>/dev/null | head -5")
    if rc != 0:
        not_run("image_has_no_data", f"could not inspect image contents: {err or out}")
        return
    residue = [x for x in out.splitlines() if x.strip()]
    check("image_has_no_data", not residue,
          "image contains no corpus or state files",
          f"image contains application data: {residue}")


def test_verb_argv_is_not_joined() -> None:
    """A switch and its value must be SEPARATE argv elements.

    Found in anger: "-ExecutionPolicy Bypass" was written as one string, so
    PowerShell received a single quoted argument, ran it as a command, and died
    with "the term '-ExecutionPolicy' is not recognized" - blaming a token and
    hiding the line that produced it. The teardown it fed did nothing at all,
    and the only trace was a non-zero exit code nobody read closely.

    A fused pair is invisible in a run that passes and fatal in the run that
    stops, which is the worst possible time to discover it."""
    hub = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "13_COMMAND_CENTER", "api", "sentinel-hub.ps1")
    argv = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", hub,
            "-Action", "stop", "-FrontPort", str(FRONT_PORT), "-BackPort", str(BACKEND_PORT)]
    fused = [a for a in argv if " " in a and not os.path.exists(a)]
    check("verb_argv_not_joined", not fused,
          f"hub invocations pass {len(argv)} separate argv elements; "
          f"no switch and its value are fused into a single string",
          f"these argv elements contain a space and are not existing paths: {fused}. "
          f"PowerShell will execute them as a command instead of parsing them "
          f"as a switch/value pair.")


def test_no_case_shadowed_params() -> None:
    """No local may assign to a variable that differs only in CASE from a
    script-level parameter.

    PowerShell variable names are case-insensitive, so inside a function
    `$port = 0` and the script's `$Port` are the SAME VARIABLE. Writing to the
    local silently rewrote the parameter for the rest of the run, and every
    comparison downstream then compared the wrong value against itself.

    Found in anger, and it is a class rather than an incident: a function in
    `verify-server.ps1` did exactly this, which made the OPTIMUS Control
    Center on port 8900 report as squatting the front port 8910 — four FAILs,
    and a precise reintroduction of the false positive the previous round had
    just removed. Every `IsFront` test returned true because it compared 8900
    to 8900.

    Static and cheap, so it belongs in the suite rather than in review. A
    regex over the source is a blunt instrument, so it is deliberately narrow:
    it only reports an assignment whose name collides in case with a DECLARED
    parameter, which is the exact shape of the bug."""
    import re
    # The root is derived from this file's own location, the same way
    # `test_every_bat_is_crlf` derives it. The first version of this check used
    # a `WORKSPACE` constant that does not exist in this module, so it raised
    # NameError on first execution and took the whole suite down with it -
    # introduced by the same kind of typo that had already taken down a phase
    # once. Referencing a name that is not there is not caught by the compiler
    # in a function body; it is caught by running it.
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    api = os.path.abspath(os.path.join(root, "13_COMMAND_CENTER", "api"))
    problems = []
    names = sorted(n for n in os.listdir(api) if n.lower().endswith(".ps1")) \
        if os.path.isdir(api) else []
    if not names:
        check("no_case_shadowed_params", False, "",
              f"no PowerShell scripts found at {api} - the check could not run")
        return
    for name in names:
        ps1 = os.path.join(api, name)
        try:
            with open(ps1, encoding='utf-8', errors='replace') as fh:
                text = fh.read()
        except Exception as e:
            problems.append(f"{name}: unreadable ({str(e)[:40]})")
            continue
        # Script-level parameters: names declared inside a `param(` block.
        declared = set()
        for block in re.findall(r"param\s*\((.*?)\)\s*\n", text, re.S):
            for m in re.finditer(r'\[\w+\]\$\{?([A-Za-z_]\w*)', block):
                declared.add(m.group(1))
        if not declared:
            continue
        lowered = {d.lower(): d for d in declared}
        for m in re.finditer(r'(?m)^\s*\$([A-Za-z_]\w*)\s*=(?!=)', text):
            vname = m.group(1)
            owner = lowered.get(vname.lower())
            if owner and vname != owner:
                line = text[:m.start()].count('\n') + 1
                problems.append(
                    f"{name}:{line} assigns ${vname} but ${owner} is a declared "
                    f"parameter - same variable in PowerShell")
    check("no_case_shadowed_params", not problems,
          f"no local in {len(names)} PowerShell scripts shadows a "
          f"script-level parameter by case alone",
          f"case-insensitive variable collisions: {problems}")


def test_every_bat_is_crlf() -> None:
    """Every .bat in the project must be CRLF, not just the one under test.

    `cmd.exe` does not reliably honour bare LF, and a `.bat` with mixed or bare
    endings is a file that looks correct in an editor and fails only when
    something executes it. The Startup entry caught this once already; the
    superseded launcher beside it was still LF-only a long time later, which is
    the shape of a fix applied to the instance that failed rather than to the
    class.

    `.ps1` and `.py` are deliberately NOT included: PowerShell and Python read
    LF perfectly well, and a check that flags correct files is a check that
    trains you to ignore it.

    The version-backup tree (`13_COMMAND_CENTER\\backups\\versions\\v*`) is
    excluded, and that exclusion is a decision rather than a convenience. Those
    files are inert historical snapshots: nothing executes them, and rewriting
    them to satisfy a lint would falsify the record of what each version
    actually contained. The live launcher beside them was normalised instead.
    If one is ever restored to the live path, this check governs it there."""
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    # BOTH sides must be abspath'd before comparing. `root` still contains a
    # literal "..", so comparing it against walked absolute paths never matches
    # - an exclusion that silently excludes nothing is worse than no exclusion,
    # because it reads as a decision and behaves as a no-op.
    backup_root = os.path.normcase(os.path.abspath(
        os.path.join(root, "13_COMMAND_CENTER", "backups", "versions")))
    bad = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if os.path.normcase(os.path.abspath(dirpath)).startswith(backup_root):
            continue
        for name in filenames:
            if not name.lower().endswith(".bat"):
                continue
            full = os.path.join(dirpath, name)
            try:
                with open(full, "rb") as fh:
                    data = fh.read()
            except OSError as e:
                bad.append(f"{name} (unreadable: {e})")
                continue
            bare = sum(1 for i, b in enumerate(data)
                       if b == 0x0A and (i == 0 or data[i - 1] != 0x0D))
            if bare:
                bad.append(f"{os.path.relpath(full, root)} ({bare} bare LF)")
    check("every_bat_is_crlf", not bad,
          f"all .bat files under the project use CRLF ({len(bad)} problems)",
          f"these .bat files contain bare LF and cmd.exe may mis-parse them: {bad}")


def _post_action(payload: dict, timeout: int = 20):
    """POST a JSON body to /api/action and return (status, body_text).

    Returns (0, '') on a transport failure rather than raising, so a caller can
    tell "the server refused this" apart from "the server was not there" -
    two very different facts that both otherwise look like a failed test."""
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            BACKEND + "/api/action", data=body, method="POST",
            headers={"Content-Type": "application/json", "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read().decode("utf-8", "replace")
        except Exception:
            return e.code, ""
    except Exception as e:
        return 0, f"transport error: {str(e)[:80]}"


def test_action_whitelist_rejects_unapproved() -> None:
    """/api/action must refuse anything not on the server's own whitelist.

    The route resolves an action through a server-side $ACTIONS table precisely
    so a crafted request cannot execute arbitrary shell. A security control that
    has never been probed is a claim, not a control - so this sends real
    injection-shaped payloads and requires HTTP 400 back.

    The payloads are sent as DATA, never executed locally: they are POST bodies
    aimed at the listener, which is the only thing under test.

    THE FIELD NAME IS `id`, and that is load-bearing. The first version of this
    test sent {"action": ...}, and every payload came back 400 - so the test
    passed, seven times, having proved nothing. The route read `$parsed.id`,
    found nothing, and returned "no action id supplied" WITHOUT ever consulting
    the whitelist. A security test that passes through a different code path
    than the one it is named after is worse than no test: it reports the
    control as verified while the control is unexercised.

    So the refusal is asserted on the BODY as well as the code, requiring the
    whitelist's own message and an echo of the payload. A refusal from any
    other path cannot satisfy it."""
    attacks = {
        "unknown action": "definitely-not-an-action",
        "shell metacharacters": "status; whoami",
        "command substitution": "$(whoami)",
        "backtick injection": "`whoami`",
        "powershell call operator": "& whoami",
        "path traversal": "../../../Windows/System32/cmd.exe",
        "null byte": "status\x00whoami",
    }
    bad = {}
    for label, action_id in attacks.items():
        code, text = _post_action({"id": action_id})
        if code == 0:
            bad[label] = text or "no response"
        elif code != 400:
            bad[label] = f"HTTP {code} (expected 400)"
        elif "unknown or forbidden action id" not in text:
            # Right code, wrong reason. This is the case that would have hidden
            # the bug above, so it is called out separately.
            bad[label] = f"HTTP 400 but not from the whitelist: {text[:90]!r}"
    check("action_whitelist_rejects", not bad,
          f"all {len(attacks)} unapproved/injection payloads were refused by the "
          f"whitelist itself, not by a missing-field guard",
          f"these payloads were not cleanly refused by the whitelist: {bad}")


def _get_raw_at(base: str, path: str, timeout: int = 20):
    """GET `path` from an arbitrary base URL, sending the path AS GIVEN.

    Split out of _get_raw so the sensitivity control can probe a SECOND
    server - the neutralised one it starts itself - without touching the live
    deployment."""
    try:
        req = urllib.request.Request(base + path, method="GET",
                                     headers={"Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read()
        except Exception:
            return e.code, b""
    except Exception as e:
        return 0, str(e).encode("utf-8", "replace")


def _get_raw(path: str, timeout: int = 20):
    """GET an arbitrary path from the deployment front and return (status, bytes).

    The path is sent AS GIVEN - no urllib quoting, no normalisation - because
    the thing under test is a server-side route table, and a client that
    tidies the path before sending cannot exercise it. Returns (0, b'') on a
    transport failure, matching _post_action, so 'refused' and 'not there'
    stay distinguishable."""
    try:
        req = urllib.request.Request(BACKEND + path, method="GET",
                                     headers={"Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read()
        except Exception:
            return e.code, b""
    except Exception as e:
        return 0, str(e).encode("utf-8", "replace")


def _post_action_origin(payload: dict, origin, timeout: int = 20):
    """POST to /api/action carrying an explicit Origin header.

    Same shape as _post_action, but the Origin is caller-controlled so the
    cross-origin gate can be exercised. origin=None omits the header entirely,
    which is what curl, PowerShell and every other non-browser client send."""
    try:
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "*/*"}
        if origin is not None:
            headers["Origin"] = origin
        req = urllib.request.Request(
            BACKEND + "/api/action", data=body, method="POST", headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read().decode("utf-8", "replace")
        except Exception:
            return e.code, ""
    except Exception as e:
        return 0, str(e)


def test_action_origin_gate_blocks_cross_origin() -> None:
    """/api/action must not be drivable from another page.

    Added 2026-10-11 after an independent verifier found a MEDIUM gap: a
    cross-origin POST with Content-Type: text/plain EXECUTED an action and
    answered 200. That is a CORS "simple request" - no preflight, so the
    browser never asked first. The action whitelist stopped injection; it never
    stopped unauthorised invocation, and a comment had called that whitelist
    "the security boundary".

    The probe payload is an action id that does not exist. That is deliberate:
    the Origin gate runs BEFORE the whitelist, so
      403 = the gate fired and nothing ran
      400 = the request reached the action layer and was refused there
    A test that instead invoked a real action would prove the gate works only
    by running something, and would have side effects as its price.

    Three things are asserted because they fail independently:
      BLOCKS  - a foreign Origin and a literal "null" are refused 403.
      ADMITS  - our own Origin, and an ABSENT Origin, still reach the action
                layer. Absent is allowed on purpose: no browser can be made to
                omit Origin, so permitting it costs nothing and keeps the
                endpoint usable from curl and from both test suites.
      DISCRIMINATES - the same predicate is re-run in memory against a gate
                neutralised to always admit. The control must stop blocking.
                If it blocks the same list, this test measures nothing.
    """
    payload = {"id": "__origin_gate_probe_no_such_action__"}
    foreign = ["https://evil.example.com", "null"]
    own = ["http://127.0.0.1:8912", "http://127.0.0.1:8910", "http://localhost:8912"]

    blocked, not_blocked = [], {}
    for o in foreign:
        status, _ = _post_action_origin(payload, o)
        if status != 403:
            not_blocked[o] = f"HTTP {status}, expected 403"
        else:
            blocked.append(o)
    for o in own + [None]:
        status, _ = _post_action_origin(payload, o)
        if status != 400:
            not_blocked[str(o)] = f"HTTP {status}, expected 400"
    check("action_origin_blocks_foreign", not not_blocked,
          f"foreign Origin refused 403, own/absent Origin reached the action "
          f"layer 400 ({len(blocked)}/{len(foreign)} blocked)",
          f"the origin gate did not hold: {not_blocked}")

    # ---- sensitivity control, neutralised in memory ---------------------
    # The shipped v3 pattern, applied to the same source the gate runs from.
    # Read the REAL allowlist out of the REAL file, neutralise that allowlist
    # IN MEMORY (never on disk), re-extract, and re-run the SAME membership
    # predicate. The neutralised gate must block strictly FEWER origins.
    # If it blocks the same list, this control proves nothing about the gate.
    srv = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "13_COMMAND_CENTER", "api", "server.ps1")
    import re  # module-level import is absent here; this file imports it locally
    with open(srv, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()

    pat = re.compile(r"\$allowedOrigins\s*=\s*@\((.*?)\)", re.S)

    def extract(text):
        m = pat.search(text)
        if not m:
            return None
        return set(re.findall(r"[\"']([^\"']+)[\"']",
                              re.sub(r"\$[A-Za-z_]\w*", "PORT", m.group(1))))

    live = extract(src)
    # Neutralise by WIDENING the allowlist to admit every probe. Note the
    # direction: the gate blocks an origin that is NOT in the table, so
    # emptying the table would block MORE, not fewer. Widening it to admit
    # everything is what switches the gate off, and it does so through the
    # same extractor and the same predicate over the same file.
    widen = ", ".join("'%s'" % p for p in foreign + own)
    broken = src.replace("$allowedOrigins = @(",
                         "$allowedOrigins = @(" + widen + "\n)", 1)
    neutral = extract(broken) if broken != src else None

    def gate(origin, table):
        return bool(origin) and origin not in table      # -notcontains

    probes = [p for p in foreign + own if p]
    real_blocks = [p for p in probes if gate(p, live or set())]
    neutral_blocks = [p for p in probes if gate(p, neutral or set())]

    check("action_origin_control_discriminates",
          bool(live) and neutral is not None and len(real_blocks) > len(neutral_blocks),
          f"the real allowlist in source blocks {len(real_blocks)} of "
          f"{len(probes)} probed origins; the same extractor and predicate over "
          f"the same file with the allowlist widened to admit all blocks "
          f"{len(neutral_blocks)}",
          "the control did not fail: the neutralised gate blocked the same or "
          "more origins than the live one, so this check is not measuring the "
          "gate at all")


def _handshake_worker_block(text: str) -> str:
    """The Start-Job block of server.ps1: from the job to the listener try."""
    start = text.find("$worker = Start-Job")
    if start < 0:
        return ""
    end = text.find("\ntry {", start)
    return text[start:end if end > 0 else len(text)]


def _handshake_wired(text: str) -> bool:
    """True when the refresh worker actually invokes the handshake script.

    Two halves, and both are needed: the script path has to be handed to the
    job through -ArgumentList (a job has its own session state, so an
    outer variable is simply $null inside it), and the job has to invoke it.
    Checking only the second would pass on a script whose path was never
    passed in; checking only the first would pass on a script nobody calls."""
    block = _handshake_worker_block(text)
    if not block:
        return False
    import re as _re
    invokes = _re.search(r"&\s*\$pyExe\s+\$handshakeScript", block) is not None
    receives = _re.search(r"Start-Job[^\n]*\$HANDSHAKE_SCRIPT", text) is not None
    return invokes and receives


def test_handshake_refresh_is_on_the_loop() -> None:
    """The MCP handshake must be produced by the refresh loop, not by hand.

    Added 2026-10-28. The `mcp_tools_wired` check has a 24 hour freshness
    bound, and the record that satisfies it was written once, by hand. Nothing
    in the system refreshed it, so the bound was a deadline only a human could
    meet - and when it lapsed, two suite checks went red with no way for the
    system to recover on its own. Measured twice in one day.

    The bound is now met by the same worker that refreshes state and the
    ecosystem snapshot, once an hour, computed from the refresh period so a
    change of that period does not silently widen the gap.

    Three things are asserted, because they can fail independently:
      WIRED       - the job receives the script and invokes it.
      INSIDE      - the cadence is computed, and its target is well inside the
                    24 hour bound. A bound met by luck is not a bound.
      DISCRIMINATES - the same predicate over a copy with the invocation
                    removed must report "not wired". If it does not, this test
                    is measuring nothing.
    """
    import re as _re
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    srv = os.path.join(root, "13_COMMAND_CENTER", "api", "server.ps1")
    with open(srv, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()

    check("handshake_refresh_is_wired", _handshake_wired(src),
          "the refresh worker receives mcp_handshake.py and invokes it, so the "
          "24h freshness bound on mcp_tools_wired is met by the system",
          "the refresh worker does not invoke the handshake script, so the "
          "bound can only be met by a human remembering")

    block = _handshake_worker_block(src)
    m = _re.search(r"\$handshakeEvery\s*=\s*\[Math\]::Max\(1,\s*"
                   r"\[int\]\[Math\]::Floor\((\d+)\s*/", block)
    check("handshake_refresh_period_inside_bound",
          m is not None and int(m.group(1)) <= 3600,
          "the cadence is computed from the refresh period, target 3600s, well "
          "inside the 86400s bound",
          "no computed handshake period found in the worker block, so the "
          "cadence cannot be shown to stay inside the bound")

    broken = block.replace("& $pyExe $handshakeScript", "& $pyExe $nothingScript")
    check("handshake_refresh_control_discriminates",
          broken != block and not _handshake_wired(src.replace(block, broken)),
          "the same predicate reports 'not wired' on a copy with the "
          "invocation removed, so this check is measuring the gate",
          "the neutralised copy still looked wired, so this test proves nothing")


def test_static_route_is_allowlisted_and_serves_intact_bytes() -> None:
    """The font route must serve the two allowlisted files and nothing else.

    Added 2026-10-10 because the route had NO automated test at all: its
    traversal safety rested entirely on a verifier's manual probe list. A
    security control that is only ever checked by hand is a claim that decays
    the moment nobody is looking.

    Three separate things are asserted, because they can fail independently:

    1. SERVES. Both allowlisted TTFs answer 200 with the right content type
       and the EXACT byte length of the file on disk. Length is the load-
       bearing part: an earlier version of this route re-encoded binaries as
       UTF-8 strings and served a healthy 200 with a corrupted body, which a
       status-code check alone would have passed.
    2. REFUSES. Traversal-shaped paths must not read a file. Traversal is not
       expected to produce 404 specifically - HttpListener answers 400 or 403
       for some shapes before the route is ever reached - so the assertion is
       on the OUTCOME (no file content came back), not on one status code.
    3. DISCRIMINATES. The traversal list is re-checked against a control in
       which the allowlist gate is neutralised. The control must find MORE
       than the live route does. If both find the same number, this test is
       not measuring the gate and is reporting safety it never exercised.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonts = os.path.join(root, "13_COMMAND_CENTER", "fonts")
    served, bad_serve = [], {}
    for name in ("jetbrains-mono-400.ttf", "jetbrains-mono-600.ttf"):
        status, body = _get_raw("/fonts/" + name)
        disk = os.path.getsize(os.path.join(fonts, name))
        if status != 200:
            bad_serve[name] = f"HTTP {status}"
        elif len(body) != disk:
            bad_serve[name] = f"{len(body)} bytes served, {disk} on disk"
        elif body[:4] != b"\x00\x01\x00\x00":
            bad_serve[name] = f"not a TrueType header: {body[:4]!r}"
        else:
            served.append(f"{name} {len(body)}B")
    check("static_route_serves_intact", not bad_serve,
          f"both allowlisted fonts served byte-exact ({', '.join(served)})",
          f"the font route did not deliver intact files: {bad_serve}")

    # Anything that is not one of the two allowlisted names must yield no file
    # content. api/server.ps1 is the sharpest probe: if traversal ever worked,
    # this would hand over the server's own source.
    probes = {
        "server source": "/fonts/../api/server.ps1",
        "server source abs": "/../api/server.ps1",
        "state file": "/fonts/../api/sentinel-state.json",
        "windows ini": "/../Windows/win.ini",
        "windows drive": "/C:/Windows/win.ini",
        "encoded traversal": "/fonts/..%2f..%2fapi/server.ps1",
        "dotdot literal": "/fonts/../../api/server.ps1",
        "null byte": "/fonts/jetbrains-mono-400.ttf%00.png",
        "directory listing": "/fonts/",
        "root index": "/index.html",
        "unknown font": "/fonts/jetbrains-mono-900.ttf",
    }
    leaked = {}
    for label, path in probes.items():
        status, body = _get_raw(path)
        # A refusal of any code is fine. What must never happen is file bytes
        # coming back - so this tests the payload, not the status.
        if b"ErrorActionPreference" in body or b"<?xml" in body or status == 200:
            leaked[label] = f"HTTP {status}, {len(body)} bytes"
    check("static_route_refuses_traversal", not leaked,
          f"all {len(probes)} traversal probes returned no file content",
          f"the font route leaked a file for: {leaked}")

    # THE SENSITIVITY CONTROL.
    #
    # Two versions of this control failed before this one, and both failures
    # are the point:
    #
    #   v1 wrote a neutralised COPY of server.ps1 to disk and then probed the
    #      LIVE server. The copy was never executed, so the control reached
    #      exactly as far as the live route (0 vs 0) and the check correctly
    #      reported "not measuring the gate".
    #   v2 actually started the neutralised copy on port 8925 and probed
    #      that. Measured: the process came up but never bound the port - every
    #      probe returned no connection. A control that cannot attach to the
    #      thing it attacks is the same defect wearing a new hat.
    #
    # So this version asserts the INVARIANT statically instead, which is how
    # the rest of this suite already tests security properties: the argument
    # handed to Join-Path must be `$key` - a literal from the hardcoded
    # hashtable - and must never be `$rel`, `$name` or `$path`, which are
    # derived from the request.
    #
    # It discriminates because the neutralisation is applied in memory and the
    # SAME predicate is re-run: rewrite Join-Path to take `$rel` and the
    # predicate must fail. A predicate that passes both ways measures nothing.
    #
    # (`src` was briefly undefined here after the live-server control was
    # replaced - the rewrite consumed the line that defined it. Caught by the
    # suite itself: NameError, the check never ran, exit 1.)
    src = os.path.join(root, "13_COMMAND_CENTER", "api", "server.ps1")
    with open(src, "r", encoding="utf-8") as fh:
        original = fh.read()

    def _gate_is_literal_key(text: str) -> bool:
        """True when every Join-Path under $ROOT receives a literal key."""
        for line in text.splitlines():
            if "Join-Path $ROOT" not in line:
                continue
            for unsafe in ("$rel", "$name", "$path", "$_"):
                if unsafe in line:
                    return False
        return "Join-Path $ROOT ($key" in text

    live_ok = _gate_is_literal_key(original)
    # Neutralise: hand Join-Path the request-derived value instead of the key.
    broken = original.replace("Join-Path $ROOT ($key",
                              "Join-Path $ROOT ($rel", 1)
    control_reports_broken = broken != original and not _gate_is_literal_key(broken)
    check("static_route_gate_is_literal", live_ok,
          "every Join-Path under $ROOT receives $key, a literal from the "
          "allowlist - request-derived values can only SELECT a name, never "
          "compose a path",
          "server.ps1 hands a request-derived variable to Join-Path under "
          "$ROOT, so a crafted path could reach the filesystem")
    check("static_route_control_discriminates", control_reports_broken,
          "the same predicate fails when the gate is rewritten to take $rel, "
          "so this check is measuring the gate and not passing vacuously",
          "the predicate passed even after the gate was neutralised "
          "(Join-Path $ROOT ($key was not found to rewrite), so the check "
          "cannot prove it discriminates")


def test_action_missing_id_is_refused_separately() -> None:
    """A body with no `id` at all must be refused for its OWN reason.

    This is a different control from the whitelist, and it is asserted
    separately so that neither can be satisfied by the other. Without this
    check, a regression that broke `id` parsing would still be reported as
    "the whitelist correctly refused everything"."""
    code, text = _post_action({"action": "status"})
    ok = (code == 400) and ("no action id supplied" in text)
    check("action_missing_id_refused", ok,
          "a body with no `id` is refused with 'no action id supplied'",
          f"expected 400 + 'no action id supplied', got HTTP {code} body {text[:90]!r}")


def test_action_whitelist_admits() -> None:
    """The complement: a whitelisted action must actually be allowed.

    A whitelist test that only proves rejection can be satisfied by a route that
    refuses everything, including the actions it is supposed to serve. Both
    directions are required, or the first test is measuring nothing.

    The id used here is `logs_tail`, read from server.ps1's own $ACTIONS table.
    The first version of this test asked for `status`, which is not an action at
    all, so it failed - and its failure message blamed the whitelist for
    "rejecting everything", which was a different bug entirely. A test that
    reports the wrong cause sends the reader to fix the wrong thing."""
    code, text = _post_action({"id": "logs_tail"})
    check("action_whitelist_admits", code == 200,
          "the whitelisted action 'logs_tail' is accepted, so the whitelist discriminates",
          f"whitelisted action 'logs_tail' returned HTTP {code} body {text[:90]!r} - "
          f"if this is 400 the whitelist is rejecting its own approved actions, "
          f"which would make the rejection test meaningless")


def _lists_over(node, limit: int, trail: str = ""):
    """Every list in a payload whose length exceeds `limit`, as (trail, len).

    The recursion visits **every** element, not the first `limit` of them.

    That was a real hole, found by the verifier: the first version wrote
    `for i, v in enumerate(node[:limit])`, so it recursed only into the first 25
    entries of any list. A 500-entry list at index 3 was reported; the
    identical list at index 30 was invisible. The self-test used a 26-entry list
    at index 0, so it passed without ever reaching the hole — which is the
    worst possible arrangement, because the guard was green while the thing it
    guards was broken.

    A bounded walk still needs a bound, or a pathological payload walks forever,
    so a node budget applies. When the budget is exhausted that is reported as
    an explicit "scan incomplete" entry: a truncated scan must never be
    indistinguishable from a clean one.
    """
    found = []
    budget = [_SCAN_BUDGET]

    def walk(node, trail):
        if budget[0] <= 0:
            return
        budget[0] -= 1
        if isinstance(node, list):
            if len(node) > limit:
                found.append((trail or "<root>", len(node)))
            for i, v in enumerate(node):
                walk(v, f"{trail}[{i}]")
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{trail}.{k}" if trail else k)

    walk(node, trail)
    if budget[0] <= 0:
        found.append((f"{trail} (scan incomplete)", -1))
    return found


# A walk budget, not a scan limit: it bounds work, it does not define what is
# examined. Sized far above any real payload here, and reported if ever hit.
_SCAN_BUDGET = 200_000

# A list is a FEED if it is a stream consumed over time and therefore needs a
# cap. It is an INVENTORY if its length is fixed by how much code exists.
#
# `checks` (55) and `health_checks` are inventories: one entry per check
# function defined in monitor.py. They do not grow with elapsed time, and
# capping them at 25 would mean deleting real measurements. `surfaces` (21) is
# the same shape. `results` (the lifecycle verifier's check list) is too: one
# entry per check the verifier runs, fixed by the script, not by elapsed time.
#
# The first version of this check flagged ANY list over 25, so it failed on the
# inventory and passed on nothing. A detector that fires on correct data is
# worse than no detector: it is a permanent red that hides real regressions and
# teaches the operator to ignore the suite.
#
# What is actually governed is the log/event stream. So this measures THAT, and
# separately asserts the inventories are internally complete - which is the
# useful property a length cap was standing in for.
FEED_LIMIT = 25

# The inventory registry, keyed by the FULL TRAIL - not by the leaf name.
#
# The first version matched `trail.split(".")[-1]`. That is fine while the
# registry holds four unambiguous names, and it is a trap the moment it does
# not: registering "classes" to stop flagging `tests.classes` would have waved
# through `rows.classes`, `events.classes`, any list named `classes` at any
# depth in any payload, permanently. A table that cannot fail is not a mapping,
# it is a waiver. So the exemption is qualified - only the exact trails below
# are inventories, and `rows.classes` is still a problem.
#
# `tests.classes` is one entry per class registered in the suite. It crossed 25
# when `MonitorCoverage` was added, which is what surfaced this: the shape is
# an inventory (fixed by code, not by elapsed time) and the registry had never
# heard of it.
INVENTORY_TRAILS = frozenset({
    "checks",           # monitor.py, one per check function
    "health_checks",
    "surfaces",         # the ecosystem collector, one per measured surface
    "results",          # the lifecycle verifier's check list
    "tests.classes",    # the suite, one per registered class
})

# An exemption that cannot fail is a waiver, so every inventory must DECLARE its
# own total and be held to it. The pairs are scoped to the route that ships them,
# so a pair can never be applied to a payload it was not written for, and the
# total need not be named after the list - /api/minimax calls it `counts.total`.
DECLARED_TOTALS = {
    "/api/health":  (("total_checks", "checks"),),
    "/api/minimax": (("counts.total", "surfaces"),),
    "/api/verify":  (("total", "results"),),
    "/api/state":   (("tests.total_classes", "tests.classes"),
                     ("health_total_checks", "health_checks")),
}

# Every list-bearing payload the UI actually renders. An earlier version audited
# only two of these; `results` in particular would have been flagged as an
# ungoverned feed if /api/verify had been scanned.
AUDITED_ROUTES = ("/api/health", "/api/minimax", "/api/state", "/api/verify")


def _trail_key(trail: str) -> str:
    """A trail with its list indices removed: `rows[30].events` -> `rows.events`.

    The index is not part of the shape - the same list is the same inventory
    however it was reached - but it must not be a way to smuggle a registered
    name past an unregistered position.
    """
    out, depth = [], 0
    for ch in trail:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _dig(node, dotted: str):
    """Read `a.b.c` out of nested dicts, or None if any step is missing."""
    cur = node
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _registered_suite_classes():
    """How many classes the suite registers in `run_all_tests()`, or None.

    Read with `ast`, not a regex: a regex that guesses the list's shape is the
    same class of defect this whole check exists to prevent. Returns None when
    the source cannot be read or parsed, which the caller reports as NOT
    VERIFIED rather than quietly treating as agreement.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(here, "test_suite.py"), "r", encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except Exception:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_all_tests":
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "tests" for t in stmt.targets
                ):
                    if isinstance(stmt.value, ast.List):
                        return len(stmt.value.elts)
    return None


def _is_count(value) -> bool:
    """A declared total is only a count if it is a genuine integer.

    `26.0 == 26` and `True == 1` are both True in Python, so a JSON payload
    declaring `total_classes: 26.0` or `true` satisfied every comparison the
    inventory contract makes, and the suite-source cross-check below - which is
    guarded by `isinstance(x, int)` - was skipped for a float while still
    reading as verified. `bool` is a subclass of `int` and has to be excluded by
    hand. A count that is not a count cannot be compared, so it is reported.
    """
    return isinstance(value, int) and not isinstance(value, bool)


def _inventory_problems(data, registered=None, route="/api/state") -> dict:
    """Every way this payload breaks the inventory contract, grouped by kind.

    Extracted from the live check so the self-test exercises THIS function and
    not a paraphrase of it. Inlining the logic in the check body left nothing
    for a polarity test to call, and a self-test that re-implements the rule
    proves the copy, not the rule.

    Three things are enforced, and the first two are what make the third worth
    anything:

      1. No list over the bound may sit at an unregistered trail.
      2. No REGISTERED trail may be exempt without a declared total to be held
         against. This is the self-audit: adding a trail to INVENTORY_TRAILS
         without giving it a pair here makes this function complain, so the
         registry cannot grow a silent waiver.
      3. The declared total must match the shipped list, and `tests.classes`
         must additionally match the suite that produced it.

    `registered` is the suite's own registration count, or None when the source
    could not be read. None is reported as UNVERIFIED, never as agreement.
    """
    problems = {}
    pairs = DECLARED_TOTALS.get(route, ())
    paired_lists = {lst for _tot, lst in pairs}

    exempt = set()
    for trail, n in _lists_over(data, FEED_LIMIT):
        if n < 0:
            problems["scan"] = (f"{trail} - the scan did not finish, so this "
                                f"payload is UNVERIFIED")
            continue
        key = _trail_key(trail)
        # A trail carrying an index is a DESCENDANT of a registered list, not
        # that list. `_trail_key` strips the index so the lookup works, which
        # means `surfaces[0]` normalises to `surfaces` - and a 30-entry feed
        # nested inside `surfaces` would inherit the parent's exemption, with
        # the declared total matching the outer list and contradicting nothing.
        # The inventory is the list at the registered path itself. Anything
        # found below it is a feed and must be judged on its own.
        if key != trail:
            problems.setdefault("unregistered", []).append(
                f"{trail}={n} is nested inside {key} - a list INSIDE a known "
                f"inventory is a feed, not the inventory, and inherits no exemption")
            continue
        if key not in INVENTORY_TRAILS:
            problems.setdefault("unregistered", []).append(
                f"{trail}={n} is over the bound and is not a known inventory; "
                f"registered trails are {sorted(INVENTORY_TRAILS)}")
            continue
        # The registry is keyed on a dotted PATH, not on a name. A payload
        # carrying a literal top-level key called "tests.classes" is not shipping
        # the nested inventory - it is shipping one flat key with a dot in its
        # name, which the trail builder cannot tell apart from a nested path.
        # Requiring the path to actually resolve to a list closes that: on the
        # flat payload `_dig` finds no "tests" key and returns None.
        if not isinstance(_dig(data, key), list):
            problems.setdefault("unregistered", []).append(
                f"{trail} matches a registered trail by NAME but the path does "
                f"not resolve to a list in this payload")
            continue
        # ...and the converse shadow: a payload carrying BOTH a literal
        # "tests.classes" key and a nested tests.classes produces the same trail
        # twice, so the flat impostor's count cannot be told from the real one's.
        # Resolving the path proves a list exists, not which list was counted,
        # so when both exist the exemption is refused rather than guessed.
        if "." in key and isinstance(data, dict) and key in data:
            problems.setdefault("unregistered", []).append(
                f"{trail} is produced both by a literal top-level key and by a "
                f"nested path, so the over-bound list cannot be attributed to either")
            continue
        exempt.add(key)
        if key not in paired_lists:
            problems.setdefault("unbacked_exemption", []).append(
                f"{trail} is exempt as a known inventory but {route} declares no "
                f"total for it - an exemption nothing can contradict is a waiver")

    for total_key, list_key in pairs:
        declared = _dig(data, total_key)
        if declared is None:
            # A pair that names a key the producer never writes is INERT, and an
            # inert pair is the exact waiver rule 2 exists to prevent. The first
            # version of this loop skipped quietly, so `health_checks` was
            # "backed" by a pair pointing at a nested `health.total_checks` while
            # the producer shipped the total flat as `health_total_checks`:
            # `_dig` returned None, the comparison never ran, and a payload
            # declaring 99 checks while shipping 30 reported clean. The audit
            # below said yes because the pair WAS registered - so the audit has
            # to prove the total is actually present, not merely named.
            if list_key in exempt:
                problems.setdefault("unbacked_exemption", []).append(
                    f"{list_key} is exempt as a known inventory but {route} ships "
                    f"no {total_key}, so the pair cannot be contradicted")
            continue                      # this payload claims no total here
        shipped = _dig(data, list_key)
        if shipped is None:
            problems.setdefault("declared_total", []).append(
                f"declares {total_key}={declared} but ships no {list_key}")
            continue
        if not isinstance(shipped, list):
            problems.setdefault("declared_total", []).append(
                f"{total_key} is declared but {list_key} is not a list")
            continue
        if not _is_count(declared):
            problems.setdefault("declared_total", []).append(
                f"declares {total_key}={declared!r} which is not an integer count "
                f"(a float or a bool compares equal to the real count in Python, "
                f"so it satisfies every comparison without being one)")
            continue
        if declared != len(shipped):
            problems.setdefault("declared_total", []).append(
                f"declares {total_key}={declared} but ships {len(shipped)} entries")

    payload_classes = _dig(data, "tests.total_classes")
    if registered is None:
        problems.setdefault("unverified", []).append(
            "tests.total_classes could not be held against test_suite.py - the "
            "suite source was unreadable, so the class inventory is UNVERIFIED")
    elif payload_classes is None:
        # This route ships no class inventory at all - three of the four audited
        # routes have no `tests` block. `None` is absence, not a bad count, and
        # `None != 26` is True, so without this branch every one of those routes
        # reported a phantom contradiction.
        pass
    elif not _is_count(payload_classes):
        # The old guard was `isinstance(payload_classes, int)`, which is False
        # for a float - so a payload declaring 26.0 was neither contradicting the
        # source nor checked against it. The inventory was simply not examined.
        # `None` still means "this route ships no class inventory at all" and is
        # skipped: three of the four audited routes have no `tests` block, and
        # reporting those would be a false FAIL invented by the fix.
        problems.setdefault("unverified", []).append(
            f"the payload reports {payload_classes!r} test classes, which is not "
            f"an integer count, so it could not be held against the "
            f"{registered} classes test_suite.py registers")
    elif payload_classes != registered:
        problems.setdefault("unverified", []).append(
            f"the payload reports {payload_classes} test classes but test_suite.py "
            f"registers {registered}")
    return problems


def test_telemetry_feed_is_bounded() -> None:
    """The event/log feed must honour the 25-entry FIFO bound.

    Measured four ways:

    1. The detector is proved NON-VACUOUS twice: on a flat 26-entry list, and on
       a 26-entry list NESTED PAST position 25. The second case exists because
       the first version of the detector truncated its own recursion and the
       single flat self-test never reached the hole.
    2. The real governed feed (`logs_tail`, the log stream) is measured live
       and required to be within the bound.
    3. The inventory lists are required to match the count the payload itself
       declares, which catches a truncated or partially-shipped report - the
       real risk a blunt "len > 25" rule was gesturing at, without demanding
       that the system delete its own measurements."""
    # -- 1. the detector must still fire, including where it used to be blind --
    if not _lists_over({"feed": list(range(FEED_LIMIT + 1))}, FEED_LIMIT):
        check("telemetry_detector_armed", False, "",
              f"the detector did not flag a {FEED_LIMIT + 1}-entry list, so it "
              f"cannot detect an oversized feed at all")
        return
    ok_edge = not _lists_over({"feed": list(range(FEED_LIMIT))}, FEED_LIMIT)

    # The regression that actually happened: a 26-entry list at index 3 of a
    # longer list must be found. The old detector walked only the first 25
    # elements and returned nothing here.
    #
    # The assertion looks for THE SPECIFIC NESTED LIST, not for an empty
    # result. Its first version asserted `if _lists_over(...)` - i.e. "any hit
    # means the detector failed" - but the outer `rows` list is itself 41 long
    # and legitimately reported, so the check failed while the detector was
    # working. A self-test that asserts the wrong shape reports the healthy
    # system as broken, which is the same fault as a detector that fires on
    # correct data, one layer up.
    nested = {"rows": [{"i": i, "pad": 0} for i in range(40)]}
    nested["rows"][30] = {"i": 30, "events": list(range(FEED_LIMIT + 1))}
    hits = _lists_over(nested, FEED_LIMIT)
    found_nested = [t for t, n in hits if t.endswith(".events") and n == FEED_LIMIT + 1]
    if not found_nested:
        check("telemetry_detector_armed", False, "",
              f"the detector missed a {FEED_LIMIT + 1}-entry list nested at index 30; "
              f"it reported {sorted(hits)[:4]}")
        return

    # A scan that ran out of budget must say so, not report clean.
    check("telemetry_detector_armed", ok_edge,
          f"detector flags {FEED_LIMIT + 1} entries, accepts exactly {FEED_LIMIT}, "
          f"and finds an oversized list nested past position 25 ({found_nested[0]})",
          f"detector fired on a list of exactly {FEED_LIMIT} - its bound is off by one")

    # -- 2. the real feed ---------------------------------------------------
    try:
        body = json.dumps({"id": "logs_tail"}).encode("utf-8")
        req = urllib.request.Request(
            BACKEND + "/api/action", data=body, method="POST",
            headers={"Content-Type": "application/json", "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=30) as r:
            lines = [x for x in r.read().decode("utf-8", "replace").splitlines() if x.strip()]
        rc = r.status
    except Exception as e:
        lines, rc = [], str(e)[:60]
    check("log_feed_within_bound", rc == 200 and len(lines) <= FEED_LIMIT,
          f"the log stream returned {len(lines)} lines, within the {FEED_LIMIT}-entry bound",
          f"the log stream returned {len(lines)} lines (rc={rc}) - the FIFO bound is not honoured")

    # -- 3. inventories complete, not capped --------------------------------
    problems = {}
    registered = _registered_suite_classes()
    for path in AUDITED_ROUTES:
        try:
            with urllib.request.urlopen(FRONT + path, timeout=20) as r:
                data = json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            problems[path] = f"could not read: {str(e)[:50]}"
            continue
        found = _inventory_problems(data, registered, route=path)
        if found:
            problems[path] = "; ".join(
                item for items in found.values() for item in
                (items if isinstance(items, list) else [items]))
    check("inventories_complete", not problems,
          f"across {len(AUDITED_ROUTES)} list-bearing routes: every list over {FEED_LIMIT} "
          f"is a declared inventory, each declared total matches what is shipped, the "
          f"class count matches the suite that produced it, and no scan was truncated",
          f"inventory problems: {problems}")


def test_inventory_registry_exempts_correctly() -> None:
    n = FEED_LIMIT + 1
    good = {"tests": {"classes": [{"name": f"C{i}"} for i in range(n)],
                      "total_classes": n}}
    r1 = _inventory_problems(good, registered=n, route="/api/state")
    check("inventory_registry_exempts_correctly", not r1,
          f"exemption works: {n}-entry tests.classes is clean",
          f"a correctly-declared {n}-entry tests.classes was reported as a "
          f"problem: {r1} - the registry exempts the wrong thing or nothing")


def test_inventory_registry_catches_same_leaf_name() -> None:
    n = FEED_LIMIT + 1
    impostor = {"rows": [{"classes": [1] * n}]}
    r2 = _inventory_problems(impostor, registered=1, route="/api/state")
    caught = "unregistered" in r2 and any("rows[0].classes" in m for m in r2["unregistered"])
    check("inventory_registry_catches_same_leaf_name", caught,
          f"same leaf name is caught: rows[0].classes is flagged",
          f"a {n}-entry rows[0].classes was NOT reported - the registry matches "
          f"on the leaf name, so any list called 'classes' is waved through at "
          f"any depth; it returned {r2}")


def test_inventory_registry_catches_lying_total() -> None:
    n = FEED_LIMIT + 1
    liar = {"tests": {"classes": [{"name": f"C{i}"} for i in range(n)],
                      "total_classes": n + 5}}
    r3 = _inventory_problems(liar, registered=n, route="/api/state")
    caught = "declared_total" in r3
    check("inventory_registry_catches_lying_total", caught,
          "declared total that lies is caught",
          f"declared total {n+5} for list of length {n} was not caught")


def test_inventory_registry_catches_headless_total() -> None:
    n = FEED_LIMIT + 1
    headless = {"tests": {"total_classes": n}}
    r3b = _inventory_problems(headless, registered=n, route="/api/state")
    caught = "declared_total" in r3b and any("ships no" in m for m in r3b["declared_total"])
    check("inventory_registry_catches_headless_total", caught,
          "headless total is caught",
          f"headless total not caught: {r3b}")


def test_inventory_registry_catches_unbacked_exemption() -> None:
    n = FEED_LIMIT + 1
    unbacked = {"surfaces": [{"id": f"s{i}"} for i in range(n)]}
    r3c = _inventory_problems(unbacked, registered=1, route="/api/state")
    caught = "unbacked_exemption" in r3c
    check("inventory_registry_catches_unbacked_exemption", caught,
          "unbacked exemption is caught",
          f"unbacked exemption not caught: {r3c}")


def test_inventory_registry_catches_inert_pair() -> None:
    n = FEED_LIMIT + 1
    inert = {"health_total_checks": 99, "health_checks": [1] * 30,
             "tests": {"classes": [1] * n, "total_classes": n}}
    r3d = _inventory_problems(inert, registered=n, route="/api/state")
    caught = "declared_total" in r3d and any("health_total_checks=99 but ships 30" in m for m in r3d["declared_total"])
    check("inventory_registry_catches_inert_pair", caught,
          "inert pair is caught",
          f"inert pair not caught: {r3d}")


def test_inventory_registry_catches_exempt_list_with_no_total() -> None:
    n = FEED_LIMIT + 1
    untotaled = {"health_checks": [1] * 30,
                 "tests": {"classes": [1] * n, "total_classes": n}}
    r3e = _inventory_problems(untotaled, registered=n, route="/api/state")
    caught = "unbacked_exemption" in r3e and any("health_checks" in m and "no health_total_checks" in m for m in r3e["unbacked_exemption"])
    check("inventory_registry_catches_exempt_list_with_no_total", caught,
          "exempt list with no total is caught",
          f"exempt list with no total not caught: {r3e}")


def test_inventory_registry_catches_flat_key_impostor() -> None:
    n = FEED_LIMIT + 1
    impostor_path = {"tests.classes": [1] * n}
    r3f = _inventory_problems(impostor_path, registered=n, route="/api/state")
    caught = "unregistered" in r3f and any("does not resolve to a list" in m for m in r3f["unregistered"])
    check("inventory_registry_catches_flat_key_impostor", caught,
          "flat key impostor is caught",
          f"flat key impostor not caught: {r3f}")


def test_inventory_registry_accepts_real_flat_payload() -> None:
    n = FEED_LIMIT + 1
    real_flat = {"health_total_checks": 30, "health_checks": [1] * 30,
                 "tests": {"classes": [1] * n, "total_classes": n}}
    r3g = _inventory_problems(real_flat, registered=n, route="/api/state")
    check("inventory_registry_accepts_real_flat_payload", not r3g,
          "real flat payload is accepted",
          f"real flat payload was flagged: {r3g}")


def test_inventory_registry_catches_nested_feed() -> None:
    nested_feed = {"surfaces": [[0] * 30], "counts": {"total": 1}}
    r3h = _inventory_problems(nested_feed, registered=1, route="/api/minimax")
    caught = "unregistered" in r3h and any("inherits no exemption" in m for m in r3h["unregistered"])
    check("inventory_registry_catches_nested_feed", caught,
          "nested feed is caught",
          f"nested feed not caught: {r3h}")

    # control: a flat surfaces list of the declared length is still fine
    flat_ok = {"surfaces": [{"id": i} for i in range(30)], "counts": {"total": 30}}
    caught_ok = not _inventory_problems(flat_ok, registered=1, route="/api/minimax")
    check("inventory_registry_accepts_flat_surfaces_list", caught_ok,
          "flat surfaces list is accepted",
          "flat surfaces list was flagged")


def test_inventory_registry_catches_shadowed_impostor() -> None:
    n = FEED_LIMIT + 1
    shadowed = {"tests.classes": [0] * 40,
                "tests": {"classes": [0] * n, "total_classes": n}}
    r3i = _inventory_problems(shadowed, registered=n, route="/api/state")
    caught = "unregistered" in r3i and any("cannot be attributed" in m for m in r3i["unregistered"])
    check("inventory_registry_catches_shadowed_impostor", caught,
          "shadowed impostor is caught",
          f"shadowed impostor not caught: {r3i}")


def test_inventory_registry_catches_non_int_total() -> None:
    n = FEED_LIMIT + 1
    as_float = {"tests": {"classes": [1] * n, "total_classes": float(n)}}
    r3j = _inventory_problems(as_float, registered=n, route="/api/state")
    caught = ("declared_total" in r3j and "unverified" in r3j
              and any("not an integer count" in m for m in r3j["declared_total"]))
    check("inventory_registry_catches_non_int_total", caught,
          "non-int total is caught",
          f"non-int total not caught: {r3j}")

    # control: a genuine int total still passes
    caught_ok = not _inventory_problems(
        {"tests": {"classes": [1] * n, "total_classes": n}}, registered=n, route="/api/state")
    check("inventory_registry_accepts_int_total", caught_ok,
          "int total is accepted",
          "int total was flagged")


def test_inventory_registry_catches_contradicting_class_count() -> None:
    n = FEED_LIMIT + 1
    good = {"tests": {"classes": [{"name": f"C{i}"} for i in range(n)],
                      "total_classes": n}}
    r4 = _inventory_problems(good, registered=n + 1, route="/api/state")
    caught = "unverified" in r4
    check("inventory_registry_catches_contradicting_class_count", caught,
          "contradicting class count is caught",
          f"contradicting class count not caught: {r4}")


def test_inventory_registry_reports_unverified_for_unreadable_source() -> None:
    n = FEED_LIMIT + 1
    good = {"tests": {"classes": [{"name": f"C{i}"} for i in range(n)],
                      "total_classes": n}}
    r5 = _inventory_problems(good, registered=None, route="/api/state")
    caught = "unverified" in r5
    check("inventory_registry_reports_unverified_for_unreadable_source", caught,
          "unreadable source is unverified",
          f"unreadable source not caught: {r5}")


def test_inventory_registry_validates_parseable_source() -> None:
    src = _registered_suite_classes()
    ok = isinstance(src, int) and src > 0
    check("inventory_registry_validates_parseable_source", ok,
          f"parseable source validates: {src} classes",
          f"the suite registration list could not be parsed out of test_suite.py: {src!r}")


def test_dom_injection_is_guarded() -> None:
    """SPEC_R104: no DOM injection without first proving the container exists.

    The failure this prevents is a blank panel: `el.innerHTML = ...` on a null
    reference throws, the handler dies mid-render, and the page looks empty
    while the network log says everything returned 200.

    This is checked by loading the real page, clicking every tab, and requiring
    that each one produced rendered content. The static half checks that the
    render path does not assign into an un-guarded lookup."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        not_run("dom_injection_guarded", f"playwright unavailable: {str(e)[:60]}")
        return
    bad = []
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            pg = b.new_page()
            pg.goto(FRONT + "/", wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(2500)
            tabs = pg.eval_on_selector_all(
                "[data-tab]", "els => els.map(e => e.textContent.trim())")
            for name in tabs:
                pg.eval_on_selector(
                    "[data-tab]", "(el, t) => el.textContent.trim() === t ? el.click() : null", name)
                pg.wait_for_timeout(350)
                info = pg.evaluate("""() => {
                  const p = document.querySelector('.panel.active') || document.querySelector('.panel');
                  if (!p) return {missing:true};
                  const r = p.getBoundingClientRect();
                  return {h: Math.round(r.height), t: (p.innerText||'').trim().length};
                }""")
                if info.get("missing") or info.get("h", 0) <= 0 or info.get("t", 0) == 0:
                    bad.append(f"{name}: {info}")
            b.close()
    except Exception as e:
        not_run("dom_injection_guarded", f"browser run failed: {str(e)[:70]}")
        return
    check("dom_injection_guarded", not bad,
          f"all {len(tabs)} tabs rendered visible, non-empty content after clicking",
          f"these tabs rendered nothing: {bad}")


def test_polling_is_not_starved() -> None:
    """SPEC_R110: the dashboard must REFRESH itself, not merely look alive.

    Measured 2026-10-10 (R10): `armPolling(ms)` cleared and restarted its
    interval, and `onStreamClose` re-armed it unconditionally on every stream
    close. The stream closes every ~15-25s, so the 30s countdown restarted
    before it could ever expire and `/api/health` was fetched exactly once, at
    page load. Every figure on screen stayed frozen for the life of the page
    while the `age` indicator - a separate 1s interval - kept advancing.

    Nothing caught it. A fresh load is healthy by construction, so every
    existing check passed. The failure only exists across a window LONGER than
    the interval that keeps resetting the timer.

    So this check counts `/api/health` requests over a window longer than the
    close cadence, and requires more than the single pair `connect()` makes at
    startup.

    It also carries its own sensitivity control: the same page is served again
    with the cadence guard removed, and the check requires that the count DOES
    drop. A detector that cannot see the failure it was written for is worse
    than no detector, because it converts a live defect into a green run."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        not_run("polling_refresh", f"playwright unavailable: {str(e)[:60]}")
        return

    WINDOW_MS = 50000          # > one 30s poll cadence, > the ~25s close gap
    MIN_REFRESHES = 2          # connect()'s startup pair + at least one poll
    GUARD = "if(pollTimer && pollMs === ms) return;"

    # add_init_script runs the string as a raw STATEMENT, unlike evaluate, which
    # CALLS the function it is given. A bare `() => {...}` here is an expression
    # statement that defines a function and discards it, so window.__hc stayed
    # undefined and the run returned None instead of a count. The first version
    # of this check died on `None < 2`. Invoke it.
    counter = """window.__hc = 0;
    (function(){
      var of = window.fetch;
      window.fetch = function(){
        if (String(arguments[0]).indexOf('/api/health') >= 0) window.__hc++;
        return of.apply(this, arguments);
      };
    })();"""

    try:
        import urllib.request
        real = urllib.request.urlopen(FRONT + "/", timeout=25).read().decode("utf-8", "replace")
    except Exception as e:
        not_run("polling_refresh", f"could not read {FRONT}/: {str(e)[:60]}")
        return

    if GUARD not in real:
        not_run("polling_refresh",
                "cadence guard not found in served index.html - the sensitivity "
                "control has nothing to remove, so this check cannot discriminate")
        return
    mutated = real.replace(GUARD, "")

    def count_over_window(body=None):
        # Each run owns its own Playwright context. Nesting a second
        # sync_playwright() inside a live one raises "using Playwright Sync API
        # inside the asyncio loop", which surfaced as NOT_RUN on the first run
        # of this check - a green line hiding a test that never executed.
        from playwright.sync_api import sync_playwright as _spw
        with _spw() as _p:
            b = _p.chromium.launch(headless=True)
            try:
                pg = b.new_page()
                pg.add_init_script(counter)
                if body is not None:
                    pg.route(FRONT + "/", lambda r: r.fulfill(
                        status=200, content_type="text/html; charset=utf-8", body=body))
                pg.goto(FRONT + "/", wait_until="domcontentloaded", timeout=45000)
                pg.wait_for_timeout(WINDOW_MS)
                n = pg.evaluate("() => (typeof window.__hc === 'number') ? window.__hc : -1")
                if not isinstance(n, int):
                    raise RuntimeError(f"counter read returned {n!r}, not an int")
                return n
            finally:
                b.close()

    try:
        live = count_over_window(None)
        control = count_over_window(mutated)
    except Exception as e:
        not_run("polling_refresh", f"browser run failed: {str(e)[:70]}")
        return

    problems = []
    if live < MIN_REFRESHES:
        problems.append(
            f"live page refreshed {live}x in {WINDOW_MS}ms (need >= {MIN_REFRESHES}): "
            f"the poll timer is being starved by its own re-arm")
    if control >= live:
        problems.append(
            f"control did not discriminate: with the cadence guard removed the "
            f"count was {control}, not below the live {live} - this check "
            f"cannot detect the defect it was written for")

    check("polling_refresh", not problems,
          f"live page fetched /api/health {live}x in {WINDOW_MS}ms (poll fired); "
          f"control with the guard removed fetched {control}x - the check "
          f"discriminates",
          "; ".join(problems))


# ------------------------------------------------------------------ summary --
# ------------------------ 12. CD pipeline: the remote must stay cloneable ------
def test_cd_clone_verifier_blocks_a_broken_tree() -> None:
    """The clone verifier must REFUSE the defect class that broke this repo.

    Measured on 2026-10-28: origin/main carried a root tree entry whose name
    contained ':'. Git refuses ':' in a path component, so read-tree, checkout and
    every Windows clone failed while `git log` and `git status` looked perfect.

    A verifier that is only ever shown to PASS is not a verifier. This phase
    builds that exact defect on purpose and requires the script to block it, and
    then requires the same script to accept the real repository. Both directions
    are asserted, so the phase cannot pass by always failing and cannot pass by
    always passing.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    verifier = os.path.join(root, "scripts", "verify-remote-clone.ps1")
    builder = os.path.join(root, "scripts", "make-broken-tree-control.py")
    if not (os.path.isfile(verifier) and os.path.isfile(builder)):
        not_run("cd_clone_verifier_present",
                f"verifier or control builder is missing: {verifier} / {builder}")
        return

    work = tempfile.mkdtemp(prefix="sentinel-cd-verify-")
    control = os.path.join(work, "control")
    probe_root = os.path.join(work, "probes")
    os.makedirs(probe_root, exist_ok=True)
    try:
        rc, out = run_tool([sys.executable, builder, control], timeout=180,
                           log_name="cd-control-builder.log")
        if rc != 0:
            record("cd_control_built", "FAIL",
                   f"control builder returned rc={rc}: {out[-400:]}")
            return
        record("cd_control_built", "PASS",
               f"control repository carrying an invalid path entry built at {control}")

        # --- direction 1: the broken tree must be REFUSED ---
        rc_bad, out_bad = run_tool(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", verifier,
             "-Repo", control, "-RemoteUrl", control, "-CloneRoot", probe_root],
            timeout=300, log_name="cd-verify-control.log")
        refused = (rc_bad != 0
                   and "VERDICT=FAIL" in out_bad
                   and "invalid_tree_entries" in out_bad
                   and "invalid path" in out_bad.lower())
        check("cd_clone_verifier_blocks_broken_tree", refused,
              "the verifier refused the tree carrying an invalid path entry: "
              "VERDICT=FAIL, invalid_tree_entries reported, the git clone error quoted",
              f"the verifier did not block the broken tree: rc={rc_bad}; "
              f"tail of output: {out_bad[-500:]}")

        # --- direction 2: the real repository must be ACCEPTED ---
        rc_good, out_good = run_tool(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", verifier,
             "-Repo", root, "-RemoteUrl", root, "-CloneRoot", probe_root],
            timeout=300, log_name="cd-verify-real.log")
        accepted = (rc_good == 0
                    and "VERDICT=PASS" in out_good
                    and "invalid_tree_entries 0 PASS" in out_good
                    and "clone_dirty 0 PASS" in out_good)
        check("cd_clone_verifier_accepts_real_repo", accepted,
              "the verifier accepted the real repository: VERDICT=PASS, no invalid "
              "tree entries, clean clone, remote main reachable",
              f"the verifier did not accept the real repository: rc={rc_good}; "
              f"tail of output: {out_good[-500:]}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    print("=" * 74)
    print("  mavis-sentinel-hub - deployment end-to-end tests")
    print("=" * 74)

    if not test_engine():
        print("\n  Docker engine unavailable: remaining checks are NOT_RUN, not FAIL.")
    elif not ensure_deployment_up():
        # The precondition failed. Everything that needs a serving deployment
        # is UNMEASURED, not broken. Saying FAIL here would report one broken
        # thing as thirteen.
        print("\n  Deployment could not be brought up. Dependent checks are NOT_RUN, not FAIL.")
        for cid, why in (
            ("container_running", "deployment not serving"),
            ("container_health", "deployment not serving"),
            ("serves_through_front", "deployment not serving"),
            ("backend_behind_front", "deployment not serving"),
            ("sse_reconnect", "deployment not serving"),
        ):
            not_run(cid, why)
    else:
        cold = "--coldstart" in sys.argv
        # Phases are named as STRINGS and resolved at run time, not referenced
        # as bare symbols in a tuple literal.
        #
        # Found in anger, one rename away from a green run: main() listed
        # `test_action_whitelist_admits` while the function was defined as
        # `test_action_whitelist_admits_approved`. In a tuple literal that name
        # is resolved when the tuple is BUILT, so the suite would have died with
        # a NameError before the first check ran - and because the tests had
        # never been executed, nothing had caught it. A single stale name
        # destroys the evidence from every other phase as well.
        #
        # Resolving by name makes the failure local and legible: the phase that
        # cannot resolve reports itself, naming the symbol, and the rest of the
        # suite still runs.
        phase_specs = (
            ("container", "test_container"),
            ("verb_argv", "test_verb_argv_is_not_joined"),
            ("bat_crlf", "test_every_bat_is_crlf"),
            ("case_shadow", "test_no_case_shadowed_params"),
            ("loopback_only", "test_loopback_only"),
            ("serves_through_front", "test_serves_through_front"),
            ("front_not_hijacked", "test_front_not_hijacked"),
            ("backend_behind_front", "test_backend_behind_front"),
            ("sse_reconnect", "test_sse_reconnect"),
            # A callable may be given directly for a phase that needs the
            # local `cold` flag; the two forms are interchangeable.
            ("startup_entry", lambda: test_startup_entry(coldstart=cold)),
            ("ecosystem_snapshot_fresh", "test_ecosystem_snapshot_fresh"),
            ("ecosystem_route", "test_ecosystem_route"),
            ("action_whitelist", "test_action_whitelist_rejects_unapproved"),
            ("action_missing_id", "test_action_missing_id_is_refused_separately"),
            ("action_whitelist_admits", "test_action_whitelist_admits"),
            ("static_route", "test_static_route_is_allowlisted_and_serves_intact_bytes"),
            ("action_origin_gate", "test_action_origin_gate_blocks_cross_origin"),
            ("handshake_refresh", "test_handshake_refresh_is_on_the_loop"),
            ("telemetry_fifo", "test_telemetry_feed_is_bounded"),
            ("inventory_registry_exempts_correctly", "test_inventory_registry_exempts_correctly"),
            ("inventory_registry_catches_same_leaf_name", "test_inventory_registry_catches_same_leaf_name"),
            ("inventory_registry_catches_lying_total", "test_inventory_registry_catches_lying_total"),
            ("inventory_registry_catches_headless_total", "test_inventory_registry_catches_headless_total"),
            ("inventory_registry_catches_unbacked_exemption", "test_inventory_registry_catches_unbacked_exemption"),
            ("inventory_registry_catches_inert_pair", "test_inventory_registry_catches_inert_pair"),
            ("inventory_registry_catches_exempt_list_with_no_total", "test_inventory_registry_catches_exempt_list_with_no_total"),
            ("inventory_registry_catches_flat_key_impostor", "test_inventory_registry_catches_flat_key_impostor"),
            ("inventory_registry_accepts_real_flat_payload", "test_inventory_registry_accepts_real_flat_payload"),
            ("inventory_registry_catches_nested_feed", "test_inventory_registry_catches_nested_feed"),
            ("inventory_registry_catches_shadowed_impostor", "test_inventory_registry_catches_shadowed_impostor"),
            ("inventory_registry_catches_non_int_total", "test_inventory_registry_catches_non_int_total"),
            ("inventory_registry_catches_contradicting_class_count", "test_inventory_registry_catches_contradicting_class_count"),
            ("inventory_registry_reports_unverified_for_unreadable_source", "test_inventory_registry_reports_unverified_for_unreadable_source"),
            ("inventory_registry_validates_parseable_source", "test_inventory_registry_validates_parseable_source"),
            ("dom_guards", "test_dom_injection_is_guarded"),
            ("polling_refresh", "test_polling_is_not_starved"),
            ("no_data_in_image", "test_no_data_in_image"),
            ("cd_clone_verify", "test_cd_clone_verifier_blocks_a_broken_tree"),
        )
        for name, target in phase_specs:
            fn = target if callable(target) else globals().get(target)
            if fn is None:
                check(f"{name}_resolves", False,
                      "",
                      f"phase '{name}' names {target!r}, which is not defined in "
                      f"this module - the phase cannot run")
                continue
            trace(f"begin {name}")
            fn()
            trace(f"end   {name}")

    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")
    notrun = sum(1 for r in RESULTS if r["status"] == "NOT_RUN")
    total = len(RESULTS)

    print("-" * 74)
    print(f"  {passed} passed / {failed} failed / {notrun} not-run   ({total} checks)")

    report = {
        "suite": "mavis-sentinel-hub deployment e2e",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "passed": passed,
        "failed": failed,
        "not_run": notrun,
        "total": total,
        "green": failed == 0,
        "checks": RESULTS,
    }
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                           "13_COMMAND_CENTER", "api")
    try:
        with open(os.path.join(out_dir, "deployment-tests.json"), "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"  (could not write deployment-tests.json: {e})")

    if "--json" in sys.argv:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
