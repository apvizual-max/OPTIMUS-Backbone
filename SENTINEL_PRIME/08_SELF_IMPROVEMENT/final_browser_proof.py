"""Final browser proof of the live Command Center (2026-10-04).

Click every tab for real and require, for each one: displayed, non-zero height,
real visible text, and no coercion artefact. A screenshot is captured but is NOT
the evidence - a screenshot of a blank page is still a successful screenshot.
"""
import asyncio
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from browser_automation import BrowserAutomation  # noqa: E402

URL = "http://127.0.0.1:8910/"
SHOTS = Path(r"C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME\09_LOGS\screenshots")
# The tabs this proof was written against. NOT the source of truth - the real
# list is read from the page's nav at run time, because a hardcoded list falls
# behind the UI silently (this one did: it omitted Ecosystem and still reported
# "11/11"). It survives as a floor, so a tab that DISAPPEARS from the app is
# still noticed rather than quietly shrinking the denominator.
TABS = ['Overview', 'Brain', 'Method', 'Axes', 'Doctrine', 'Program',
        'Workflow', 'Tests', 'Wiring', 'Learning', 'Ecosystem', 'Cockpit']
ARTEFACTS = ("[object Object]", "undefined", "NaN", "[object HTML",
             "No runtime handshake has been performed")


async def main() -> int:
    ba = BrowserAutomation(headless=True)
    await ba.start()
    failures, errors = [], []
    try:
        page = await ba._context.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(f"console.error: {m.text}")
                if m.type == "error" else None)
        resp = await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        await asyncio.sleep(2)
        print(f"http {resp.status if resp else '?'}   title: {await page.title()!r}")
        print()

        # The tab list is read FROM THE PAGE, not hardcoded here.
        #
        # It used to be a literal list of 11 names, and it had fallen one tab
        # behind the app: Ecosystem was never clicked, never measured, never
        # checked for coercion - and the summary line compared the list against
        # itself ("11/11"), so it reported full coverage while covering less
        # than the whole UI. A proof that grades itself against its own
        # expectation cannot notice that the world moved.
        #
        # Reading the nav makes the count falsifiable: it is now whatever the app
        # actually has, and adding a panel cannot leave the proof behind.
        tabs = await page.evaluate(
            "() => Array.from(document.querySelectorAll('nav button[data-tab]'))"
            ".map(b => b.textContent.trim()).filter(Boolean)")
        if not tabs:
            print("VERDICT: NO TABS FOUND - the navigation did not render.")
            print("  An empty list is a failure, not a vacuous 0/0 pass.")
            return 1
        missing = sorted(set(TABS) - set(tabs))
        if missing:
            # TABS is now only a floor, not the source of truth: it records the
            # tabs this proof was written against, so a tab that disappears is
            # still noticed.
            failures.append(f"tabs this proof expected but the page does not have: {missing}")
        print(f"{'tab':<10} {'h':>6} {'chars':>6}  verdict")
        print("-" * 42)

        for tab in tabs:
            await page.evaluate(
                "(n) => document.querySelector(`nav button[data-tab=\"${n}\"]`).click()", tab)
            await asyncio.sleep(1.0)
            info = await page.evaluate("""
                (n) => { const p = document.getElementById('p-'+n);
                         const cs = getComputedStyle(p), r = p.getBoundingClientRect();
                         return {d: cs.display, h: Math.round(r.height), t: p.innerText}; }
            """, tab)
            bad = [m for m in ARTEFACTS if m in info["t"]]
            if info["d"] == "none" or info["h"] == 0:
                v, why = "BLANK", "not displayed"
            elif len(info["t"].strip()) < 40:
                v, why = "EMPTY", f"{len(info['t'].strip())} chars"
            elif bad:
                v, why = "ARTEFACT", str(bad)
            else:
                v, why = "renders", ""
            if v != "renders":
                failures.append(f"{tab}: {why}")
            print(f"{tab:<10} {info['h']:>6} {len(info['t'].strip()):>6}  {v}")

        await page.evaluate(
            "() => document.querySelector('nav button[data-tab=\"Overview\"]').click()")
        await asyncio.sleep(1.5)
        shot = SHOTS / "command_center_live.png"
        await page.screenshot(path=str(shot), full_page=True)

        print()
        print(f"JS errors : {len(errors)}")
        print(f"screenshot: {shot} ({shot.stat().st_size} bytes)")
        if failures or errors:
            print("VERDICT: DEGRADED")
            for f in failures:
                print(f"  - {f}")
            for e in errors[:5]:
                print(f"  - {e[:140]}")
            return 1
        print(f"VERDICT: {len(tabs)}/{len(tabs)} tabs render, 0 JS errors, no coercion")
        return 0
    finally:
        await ba.stop()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
