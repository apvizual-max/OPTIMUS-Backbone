#!/usr/bin/env python
"""
minimax_client.py -- Python-level access to MiniMax from Mavis/OPTIMUS.

WHY THIS EXISTS
---------------
Popy asked for a Python `minimax` package. Two candidates on PyPI are both
wrong, so neither was installed:

  * `minimax`          v0.0.2  "A configurable minimax package"
                                  github.com/bergurtareqtamimi/minimax_package
                                  -> NOT MiniMax AI. An unrelated third-party
                                     name-squat. Installing it would shadow
                                     this module for no benefit.
  * `minimax-python`   v0.2.0  "Unofficial Python library for the Minimax
                                  REST API", github.com/jesuscopado
                                  -> unofficial, pre-1.0, and targets a REST
                                     surface OPTIMUS does not use.

WHAT OPTIMUS ACTUALLY TALKS TO
------------------------------
Hermes is configured with:
    base_url : https://api.minimax.io/anthropic
    default  : MiniMax-M3
    api_mode : anthropic_messages
    provider : minimax-oauth   (OAuth login)  or  minimax  (MINIMAX_API_KEY)

That is the Anthropic Messages API shape. So this module speaks exactly that,
using the official `anthropic` SDK when installed and falling back to plain
httpx (already present) otherwise. Same endpoint, same models, same
credentials as Hermes -- no parallel universe.

USAGE
    minimax_client.py doctor
    minimax_client.py models
    minimax_client.py ask "your prompt" [--model MiniMax-M3]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

BASE_URL = os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.io/anthropic")
DEFAULT_MODEL = os.environ.get("MINIMAX_MODEL", "MiniMax-M3")
HERMES_ENV = r"C:\Users\apviz\AppData\Local\hermes\.env"
HERMES_AUTH = r"C:\Users\apviz\AppData\Local\hermes\auth.json"


# ------------------------------------------------------------- credentials --
def _read_dotenv(path: str) -> dict[str, str]:
    """Minimal .env reader. Hermes keeps MINIMAX_API_KEY here."""
    out: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                out[k.strip()] = v
    except OSError:
        pass
    return out


def credentials() -> dict[str, Any]:
    """
    Collect every credential source OPTIMUS knows about, in priority order.

    Hermes has TWO MiniMax providers and they do NOT share credentials:
      minimax        -> API key in the environment
      minimax-oauth  -> OAuth login stored in the auth store, no env var
    """
    dotenv = _read_dotenv(HERMES_ENV)
    api_key = os.environ.get("MINIMAX_API_KEY") or dotenv.get("MINIMAX_API_KEY")

    oauth_present = False
    oauth_detail = "auth.json not found"
    try:
        with open(HERMES_AUTH, "r", encoding="utf-8", errors="replace") as fh:
            data = json.load(fh)
        blob = json.dumps(data).lower()
        oauth_present = "minimax" in blob and ("oauth" in blob or "access_token" in blob)
        oauth_detail = "found" if oauth_present else "no minimax oauth entry"
    except (OSError, json.JSONDecodeError) as e:
        oauth_detail = f"unreadable: {type(e).__name__}"

    return {
        "api_key_present": bool(api_key),
        "api_key_source": "MINIMAX_API_KEY env" if os.environ.get("MINIMAX_API_KEY")
                          else (f"{HERMES_ENV}" if dotenv.get("MINIMAX_API_KEY") else None),
        "oauth_present": oauth_present,
        "oauth_detail": oauth_detail,
        "base_url": BASE_URL,
        "default_model": DEFAULT_MODEL,
        "anthropic_sdk": _has_anthropic(),
        "httpx": _has_httpx(),
    }


def _has_anthropic() -> bool:
    try:
        import anthropic  # noqa: F401
        return True
    except ImportError:
        return False


def _has_httpx() -> bool:
    try:
        import httpx  # noqa: F401
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------- transport --
def ask(prompt: str, model: str | None = None, max_tokens: int = 1024,
        system: str | None = None) -> dict[str, Any]:
    """
    Send one prompt to MiniMax over the Anthropic Messages shape.

    Prefers the official `anthropic` SDK; falls back to httpx so the module is
    useful even where the SDK is not installed.
    """
    model = model or DEFAULT_MODEL
    creds = credentials()
    if not creds["api_key_present"]:
        return {
            "ok": False,
            "error": "no MINIMAX_API_KEY available (env, and %s)" % HERMES_ENV,
            "hint": "Hermes reaches MiniMax through the 'minimax-oauth' provider, "
                    "which stores its token in the auth store and exposes no env "
                    "var. Either export MINIMAX_API_KEY or call this through "
                    "Hermes, which already holds the OAuth session.",
            "credentials": creds,
        }

    key = os.environ.get("MINIMAX_API_KEY") or _read_dotenv(HERMES_ENV).get("MINIMAX_API_KEY", "")
    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]

    if creds["anthropic_sdk"]:
        import anthropic
        client = anthropic.Anthropic(api_key=key, base_url=BASE_URL)
        kwargs: dict[str, Any] = {"model": model, "max_tokens": max_tokens, "messages": messages}
        if system:
            kwargs["system"] = system
        r = client.messages.create(**kwargs)
        return {
            "ok": True, "transport": "anthropic-sdk", "model": r.model,
            "stop_reason": r.stop_reason,
            "text": "".join(b.text for b in r.content if getattr(b, "type", "") == "text"),
        }

    if creds["httpx"]:
        import httpx
        body: dict[str, Any] = {"model": model, "max_tokens": max_tokens, "messages": messages}
        if system:
            body["system"] = system
        r = httpx.post(
            f"{BASE_URL}/v1/messages",
            json=body,
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            timeout=120.0,
        )
        if r.status_code >= 400:
            return {"ok": False, "status": r.status_code, "error": r.text[:600]}
        d = r.json()
        return {
            "ok": True, "transport": "httpx", "model": d.get("model"),
            "stop_reason": d.get("stop_reason"),
            "text": "".join(b.get("text", "") for b in d.get("content", [])
                            if b.get("type") == "text"),
        }

    return {"ok": False, "error": "neither the anthropic SDK nor httpx is installed"}


# --------------------------------------------------------------------- CLI --
def main() -> int:
    ap = argparse.ArgumentParser(description="MiniMax client for OPTIMUS")
    ap.add_argument("action", choices=["doctor", "ask"])
    ap.add_argument("prompt", nargs="*",
                    help="the prompt. Use '-' to read it from stdin, which is the "
                         "only safe form for multi-line or quoted text: Windows "
                         "mangles a native argument that contains newlines or "
                         "double quotes, and argparse then reports a bare 'usage:'.")
    ap.add_argument("--model", default=None)
    ap.add_argument("--max-tokens", type=int, default=1024)
    a = ap.parse_args()

    if a.action == "doctor":
        print(json.dumps(credentials(), indent=2))
        return 0

    if a.prompt and a.prompt[0] == "-":
        # read the whole prompt from stdin
        prompt = sys.stdin.read()
    else:
        prompt = " ".join(a.prompt)
    if not prompt.strip():
        print("error: ask needs a prompt (pass one, or '-' to read stdin)",
              file=sys.stderr)
        return 2

    res = ask(prompt, model=a.model, max_tokens=a.max_tokens)
    if res.get("ok"):
        print(res.get("text", ""))
    else:
        print(json.dumps(res, indent=2), file=sys.stderr)
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
