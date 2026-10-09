"""
write_response.py
=================
Helper to write a completed task response to the Antigravity bridge outbox.
Call this after executing a task from Hermes.

Usage (from Python code or interactive):
    from write_response import write_response
    write_response(
        task_id="task_1783870000000_abc12345",
        result="Full result text here...",
        success=True,
        summary="Brief summary of what was done",
        artifacts=["C:/path/to/created/file.md"]
    )

Or run directly for testing:
    python write_response.py --task-id task_... --result "done" --summary "test"
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

BRIDGE_ROOT = Path(r"C:\Users\apviz\AppData\Local\hermes\pairing\antigravity")
INBOX = BRIDGE_ROOT / "inbox"
OUTBOX = BRIDGE_ROOT / "outbox"


def write_response(
    task_id: str,
    result: str,
    success: bool = True,
    summary: str = None,
    artifacts: list = None,
    agent: str = "antigravity"
) -> dict:
    """
    Write a completed task response to the outbox and remove from inbox.
    
    Args:
        task_id:   The task_id from the incoming task JSON
        result:    Full result text (can be long)
        success:   True = completed, False = failed
        summary:   Short 100-200 char summary (auto-generated from result if None)
        artifacts: List of absolute paths to any files created
        agent:     Identity of the responder (default: "antigravity")
    
    Returns:
        The response dict that was written
    """
    OUTBOX.mkdir(parents=True, exist_ok=True)

    response = {
        "task_id": task_id,
        "status": "completed" if success else "failed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "summary": summary if summary else (result[:200] + "..." if len(result) > 200 else result),
        "artifacts": artifacts or [],
        "agent": agent
    }

    outbox_file = OUTBOX / f"{task_id}.json"
    outbox_file.write_text(
        json.dumps(response, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Remove from inbox (task is now being processed / complete)
    inbox_file = INBOX / f"{task_id}.json"
    if inbox_file.exists():
        inbox_file.unlink()
        print(f"[BRIDGE] Task removed from inbox: {task_id}")

    print(f"[BRIDGE] Response written to outbox: {task_id}")
    print(f"[BRIDGE] Status: {'COMPLETED' if success else 'FAILED'}")
    print(f"[BRIDGE] Summary: {response['summary'][:100]}")

    return response


def write_error_response(task_id: str, error: str) -> dict:
    """Convenience method for writing a failure response."""
    return write_response(
        task_id=task_id,
        result=f"Task failed with error: {error}",
        success=False,
        summary=f"FAILED: {error[:150]}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--summary", default=None)
    parser.add_argument("--success", type=bool, default=True)
    parser.add_argument("--artifacts", nargs="*", default=[])
    args = parser.parse_args()

    write_response(
        task_id=args.task_id,
        result=args.result,
        success=args.success,
        summary=args.summary,
        artifacts=args.artifacts
    )
