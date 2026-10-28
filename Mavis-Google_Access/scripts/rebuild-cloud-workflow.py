#!/usr/bin/env python3
"""rebuild-cloud-workflow.py - compose the Cloud workflow from the version
that PASSED, plus the ExtendLM additions.

MEASURED 2026-10-27: publishing the local repo copy of cloud/google-access.yml
over the Cloud file REGRESSED the BOM strip. The version that had passed
(blob bbb3b162) carried
  - a diagnostic step that counts the secret shape, never its value, and
  - `sed '1s/^\\xEF\\xBB\\xBF//'` before `base64 -d`,
and the local copy carried neither, so the run failed with "base64: invalid
input". A workflow is not a file to be copied around: it is the piece that has
to be proven. This script composes from the proven version, asserts every
anchor it replaces, and refuses to write a file that lost a measured property.
"""
import sys

REPO = r"C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access"
PREV = REPO + r"\state\tmp\cloud-prev-workflow.yml"
DEST = REPO + r"\cloud\google-access.yml"

EXTENDLM_STEP = """      - name: Materialize the ExtendLM credential from the secret
        env:
          GOOGLE_EXTENDLM_CREDENTIAL_B64: ${{ secrets.GOOGLE_EXTENDLM_CREDENTIAL_B64 }}
        run: |
          # Optional on purpose: without the secret the probe reports notebooklm
          # as REFUSED, it does not fail the run.
          if [ -z "$GOOGLE_EXTENDLM_CREDENTIAL_B64" ]; then
            echo "EXTENDLM_SECRET=absent (notebooklm stays REFUSED)"
            exit 0
          fi
          # Same BOM guard as the Google credential: the decoder dies on a
          # leading ef bb bf, so the value is stripped before it is decoded.
          printf '%s' "$GOOGLE_EXTENDLM_CREDENTIAL_B64" | sed '1s/^\\xEF\\xBB\\xBF//' | tr -d '\\r\\n' | base64 -d > _src/data/extendlm.json
          if [ ! -s _src/data/extendlm.json ]; then
            echo "FATAL=extendlm secret missing or empty"
            exit 1
          fi
          node -e 'const c=require("./_src/data/extendlm.json");console.log("EXTENDLM_FIELDS="+Object.keys(c).join(",")+"token_len="+String(c.token||"").length+"refresh="+(c.refresh_token?"yes":"no"))'

"""

RUN_OLD = """      - name: Start the container
        run: |
          docker run -d --name Google_Access --restart unless-stopped \\
            -p 127.0.0.1:8766:8766 -e GA_PORT=8766 \\
            -v "$PWD/_src/data:/data" google-access:cloud
"""

RUN_NEW = """      - name: Start the container
        run: |
          # GA_EXTENDLM_NO_REFRESH=1: the host owns the ExtendLM refresh token
          # and rotates it. A second rotation from the Cloud would invalidate
          # the host copy, so the Cloud only ever consumes the snapshot.
          docker run -d --name Google_Access --restart unless-stopped \\
            -p 127.0.0.1:8766:8766 -e GA_PORT=8766 -e GA_EXTENDLM_NO_REFRESH=1 \\
            -v "$PWD/_src/data:/data" google-access:cloud
"""


def main():
    with open(PREV, encoding="utf-8") as fh:
        text = fh.read()

    problems = []

    # 1. the proven properties must survive the composition
    if "sed '1s/^\\xEF\\xBB\\xBF//'" not in text:
        problems.append("ANCHOR_MISSING bom_strip")
    if "Diagnose the secret shape" not in text:
        problems.append("ANCHOR_MISSING diagnostic_step")

    # 2. add the ExtendLM materialization before the build step
    anchor = "      - name: Build the image\n"
    if anchor not in text:
        problems.append("ANCHOR_MISSING build_step")
    elif "Materialize the ExtendLM credential" not in text:
        text = text.replace(anchor, EXTENDLM_STEP + anchor, 1)

    # 3. the Cloud instance must never rotate the shared refresh token
    if RUN_OLD not in text:
        problems.append("ANCHOR_MISSING docker_run")
    else:
        text = text.replace(RUN_OLD, RUN_NEW, 1)

    # 4. the composed file must keep every measured property
    checks = {
        "bom_strip_credentials": "sed '1s/^\\xEF\\xBB\\xBF//' | tr -d '\\r\\n' | base64 -d > _src/data/credentials.json" in text,
        "bom_strip_extendlm": "sed '1s/^\\xEF\\xBB\\xBF//' | tr -d '\\r\\n' | base64 -d > _src/data/extendlm.json" in text,
        "diagnostic_step": "Diagnose the secret shape" in text,
        "extendlm_step": "Materialize the ExtendLM credential" in text,
        "no_refresh_flag": "-e GA_EXTENDLM_NO_REFRESH=1" in text,
        "probe_step": "probe-services.mjs" in text,
    }

    # The trigger set is read from the PARSED structure, never from the text:
    # the word "pull_request" also appears in a comment that explains why the
    # workflow must not run on pull requests. A substring check would have
    # flagged the correct file, and a check that flags correct work is a
    # defect of the same class as a check that cannot fail.
    try:
        import yaml

        doc = yaml.safe_load(text)
        triggers = doc.get("on", doc.get(True))  # YAML 1.1 reads "on" as True
        if not isinstance(triggers, dict):
            problems.append("TRIGGERS_UNREADABLE")
        else:
            checks["no_pull_request_trigger"] = "pull_request" not in triggers
            checks["has_workflow_dispatch"] = "workflow_dispatch" in triggers
            checks["no_pull_request_target"] = "pull_request" not in (
                triggers.get("push", {}) or {}
            )
    except ImportError:
        problems.append("ANCHOR_MISSING yaml_parser (cannot verify the trigger set)")
    except Exception as exc:  # pragma: no cover - defensive
        problems.append("TRIGGERS_UNREADABLE %s" % exc)
    for name, ok in checks.items():
        if not ok:
            problems.append("PROPERTY_LOST " + name)

    if problems:
        for p in problems:
            print("  " + p)
        print("PROBLEMS=%d REFUSED (file not written)" % len(problems))
        return 2

    with open(DEST, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("WROTE=%s bytes=%d" % (DEST, len(text.encode("utf-8"))))
    for name in sorted(checks):
        print("PROPERTY_OK %s" % name)
    print("PROBLEMS=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
