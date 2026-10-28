# -*- coding: utf-8 -*-
"""Verificare §3 pe pagina vie: randare pe ecran, zero erori de consola.

Standardul de dovezi din proiect: scrierea unui fisier nu este suficient -
interfata trebuie sa se randeze si sa nu aiba erori in consola browserului.

Scriptul deschide pagina reala, apasa pe toate cele 13 tab-uri, si raporteaza
mesajele de consola si cererile de retea care nu sunt 200.
"""
import json
import sys

URL = "http://127.0.0.1:8910/"


def main():
    from playwright.sync_api import sync_playwright

    console = []
    network = []
    tabs = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda m: console.append({"type": m.type, "text": m.text[:300]}))
        page.on("pageerror", lambda e: console.append({"type": "pageerror", "text": str(e)[:300]}))
        page.on("response", lambda r: network.append({"url": r.url, "status": r.status}))
        page.goto(URL, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(1500)

        for t in page.query_selector_all("[role=tab]"):
            name = (t.inner_text() or "").strip()
            t.click()
            page.wait_for_timeout(350)
            panel = page.query_selector("#p-" + name.replace(" ", "-"))
            tabs.append({
                "tab": name,
                "selected": t.get_attribute("aria-selected"),
                "panel_found": panel is not None,
                "visible": panel.is_visible() if panel else False,
                "text_len": len((panel.inner_text() if panel else "").strip()),
            })

        fonts = page.evaluate("() => document.fonts.check('12px \"JetBrains Mono\"')")
        header = page.evaluate(
            "() => (document.querySelector('header')||{}).innerText || ''")
        browser.close()

    bad_net = [n for n in network if n["status"] >= 400]
    errors = [c for c in console if c["type"] in ("error", "pageerror", "warning")]
    empty = [t for t in tabs if not t["visible"] or t["text_len"] == 0]

    out = {
        "url": URL,
        "tabs_total": len(tabs),
        "tabs_empty_or_hidden": empty,
        "font_loaded": fonts,
        "console_messages_total": len(console),
        "console_errors_and_warnings": errors,
        "network_requests": len(network),
        "network_not_2xx": bad_net,
        "header": " ".join(header.split())[:180],
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if (not empty and not errors and not bad_net and len(tabs) == 13) else 1


if __name__ == "__main__":
    sys.exit(main())
