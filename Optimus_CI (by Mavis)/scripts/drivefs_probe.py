#!/usr/bin/env python3
# drivefs_probe.py - measure what Google Drive for Desktop actually knows.
#
# THREE QUESTIONS, THREE SOURCES OF TRUTH
#
# 1. Does the folder exist IN THE DRIVE?
#    Source: the cloud-side index, metadata_sqlite_db -> items table.
#    A row carries the Drive id (cloud_id) and the ancestor chain, so a
#    folder that is really in the Drive can be proven, not assumed.
#
# 2. Is the local mirror root CONNECTED?
#    Source: the DriveFS logs, the MirrorRoots announcements. The file
#    NAME is not the evidence: DriveFS rotates its logs, so the live
#    session can be writing to a numbered file while a fresh drive_fs.txt
#    holds the trace of a launch that failed. The newest announcement
#    wins, and the report says which log it came from and how old that
#    log's last write is.
#    MEASURED 2026-10-27: the "GDrive" root (E:\Google\GDrive, is_my_drive)
#    reports connected=false, while every C: root reports connected=true.
#    A disconnected root transports NOTHING - neither up nor down. That is
#    the difference between "the file is in the Drive" and "the file can
#    reach the Drive".
#
# 3. Is a given file actually there?
#    Source: the same index, by local_title, plus the ancestor chain so a
#    same-named file in another folder cannot pass for it.
#
# A measurement that cannot fail is not a measurement. This probe exits
# non-zero when it finds NOTHING, and the selfcheck proves both directions.
#
# Usage:
#   python drivefs_probe.py --pending
#   python drivefs_probe.py --title "<name>"
#   python drivefs_probe.py --root-state
#
# Exit codes:
#   0 = found (or the question was answered)
#   2 = not found - the honest answer, not a failure of the tool
#   3 = the DriveFS state could not be read at all
#
# ASCII ONLY. No BOM.

import os
import re
import sqlite3
import sys
import time

DRIVEFS_ROOT = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~/AppData/Local")),
    "Google",
    "DriveFS",
)
LOGS = os.path.join(DRIVEFS_ROOT, "Logs")

ITEM_COLS = (
    "stable_id, id, mime_type, is_folder, local_title, file_size, modified_date"
)


def find_db():
    """The cloud-side metadata database, under the signed-in account folder."""
    if not os.path.isdir(DRIVEFS_ROOT):
        return None
    candidates = []
    for name in os.listdir(DRIVEFS_ROOT):
        db = os.path.join(DRIVEFS_ROOT, name, "metadata_sqlite_db")
        if os.path.isfile(db):
            candidates.append(db)
    if not candidates:
        return None
    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates[0]


def connect_ro(path):
    uri = "file:" + path.replace("\\", "/") + "?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=15)
    con.execute("PRAGMA query_only=ON")
    return con


def safe(value, limit=400):
    if isinstance(value, bytes):
        return "<bytes %d>" % len(value)
    return str(value)[:limit]


def candidate_logs():
    """Every drive_fs log, newest first by mtime.

    MEASURED 2026-10-27: DriveFS rotates its logs. The active session was
    writing drive_fs_507.txt while a fresh drive_fs.txt held the trace of
    a launch that FAILED (CANNOT_START_IPC). A probe that reads one fixed
    filename therefore reports UNKNOWN while the system is perfectly
    healthy - a false negative that hides a working transport.
    """
    if not os.path.isdir(LOGS):
        return []
    out = []
    try:
        names = os.listdir(LOGS)
    except OSError:
        return []
    for name in names:
        if not name.startswith("drive_fs") or not name.endswith(".txt"):
            continue
        path = os.path.join(LOGS, name)
        try:
            out.append((os.path.getmtime(path), path))
        except OSError:
            continue
    out.sort(reverse=True)
    return [p for _, p in out]


def file_stamp(path):
    """The log file's own write time, as an ISO stamp comparable with the
    timestamps inside the log lines (which are UTC).

    A log's content is never newer than the file's last write, so a file
    whose write time is older than the best announcement found so far
    cannot contain a newer one - and can be skipped.
    """
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return ""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(mtime))


def report_root_state():
    """The GDrive mirror root and whether it is connected.

    The truth is the NEWEST MirrorRoots announcement about the GDrive
    root, across all logs, ordered by the timestamp inside the line - not
    by file name and not by file mtime. A file's mtime only says when it
    was last touched; the line's own timestamp says when the state was
    announced.
    """
    logs = candidate_logs()
    if not logs:
        print("ROOT_STATE=UNKNOWN")
        print("REASON=no drive_fs log under " + LOGS)
        return 3

    best_ts = ""
    best_state = "UNKNOWN"
    best_root = ""
    best_log = ""
    connected_true = 0
    connected_false = 0
    for path in logs:
        # Files are ordered newest first. Once the best announcement is
        # newer than a file's own last write, no remaining file can beat
        # it - so the scan stops there instead of reading every archive.
        fstamp = file_stamp(path)
        if best_ts and fstamp and fstamp < best_ts:
            break
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
        except OSError:
            continue
        text = raw.decode("utf-8", "replace")
        file_ts = ""
        file_state = ""
        file_root = ""
        for line in text.splitlines():
            if "MirrorRoots" not in line:
                continue
            stamp = ""
            ts_m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", line)
            if ts_m:
                stamp = ts_m.group(1)
            # Every SyncRoot in the line is a separate root. The old code
            # took the FIRST title and the FIRST connected= in the line,
            # which can belong to DIFFERENT roots - so it could report the
            # GDrive root with another root's connection state.
            for chunk in line.split("[SyncRoot:")[1:]:
                m = re.search(r'title="([^"]*)"', chunk)
                c = re.search(r"connected=(true|false)", chunk)
                if not c:
                    continue
                if c.group(1) == "true":
                    connected_true += 1
                else:
                    connected_false += 1
                if not m or m.group(1) != "GDrive":
                    continue
                r = re.search(r'root_path="([^"]*)"', chunk)
                rpath = r.group(1) if r else ""
                # Within one file the newest announcement wins; on equal
                # stamps the later line in the file wins.
                if stamp >= file_ts:
                    file_ts = stamp
                    file_state = c.group(1)
                    file_root = rpath
        if file_ts and file_ts > best_ts:
            best_ts = file_ts
            best_state = file_state
            best_root = file_root
            best_log = path

    print("ROOT_STATE=" + best_state)
    print("GDRIVE_ROOT_PATH=" + safe(best_root, 200))
    print("ROOTS_CONNECTED_TRUE=%d" % connected_true)
    print("ROOTS_CONNECTED_FALSE=%d" % connected_false)
    print("ROOT_STATE_TS=" + best_ts)
    print("LOG=" + best_log)
    print("LOGS_SCANNED=%d" % len(logs))
    if best_state == "UNKNOWN":
        print("REASON=no MirrorRoots announcement about the GDrive root in any log")
        return 3
    return 0


def ancestors(con, stable_id, depth=8):
    chain = []
    cur = stable_id
    for _ in range(depth):
        row = con.execute(
            "SELECT p.parent_stable_id FROM stable_parents p WHERE p.item_stable_id = ? LIMIT 1",
            (cur,),
        ).fetchone()
        if row is None:
            break
        parent = row[0]
        if parent is None or parent == cur:
            break
        pr = con.execute(
            "SELECT local_title FROM items WHERE stable_id = ? LIMIT 1", (parent,)
        ).fetchone()
        if pr is None:
            break
        chain.append(pr[0])
        cur = parent
    return chain


def print_items(con, rows):
    for row in rows:
        print(
            "ITEM stable_id=%s cloud_id=%s mime=%s is_folder=%s title=%s size=%s modified=%s"
            % (
                safe(row[0], 20),
                safe(row[1], 80),
                safe(row[2], 60),
                safe(row[3], 5),
                safe(row[4], 120),
                safe(row[5], 20),
                safe(row[6], 20),
            )
        )
        print("    path: " + " > ".join(list(reversed(ancestors(con, row[0]))) + [row[4]]))


def report_staleness(con, title, folder_title, local_dir):
    """How old is the copy the Cloud would actually read?

    The lag proxy compares the newest confirmed upload with the newest local
    write. That is an approximation. This is the direct measurement: the
    cloud-side item (its modified_date) compared with the local file's mtime.
    A positive LOCAL_NEWER_MIN means the cloud copy is OLDER than what is on
    disk - the Cloud instance would read a stale snapshot.
    """
    rows = con.execute(
        "WITH RECURSIVE d(stable_id) AS ("
        "  SELECT stable_id FROM items WHERE local_title = ?"
        "  UNION"
        "  SELECT p.item_stable_id FROM stable_parents p JOIN d"
        "    ON p.parent_stable_id = d.stable_id"
        ") SELECT i.stable_id, i.id, i.modified_date, i.file_size, i.local_title"
        " FROM items i JOIN d ON i.stable_id = d.stable_id"
        " WHERE i.local_title = ? AND i.is_folder = 0",
        (folder_title, title),
    ).fetchall()

    print("LOOKUP=staleness")
    print("NEEDLE=" + safe(title, 400))
    print("FOLDER=" + safe(folder_title, 300))

    chosen = None
    for r in rows:
        chain = ancestors(con, r[0])
        if folder_title in chain:
            chosen = r
            break
    if chosen is None:
        print("CLOUD_PRESENT=false")
        print("CLOUD_AGE_DAYS=UNKNOWN - nu exista in indexul de cloud")
        return 2

    cloud_ms = chosen[2] or 0
    print("CLOUD_PRESENT=true")
    print("CLOUD_MODIFIED_MS=" + str(cloud_ms))
    print("CLOUD_SIZE=" + safe(chosen[3], 20))
    print("CLOUD_ID=" + safe(chosen[1], 80))

    local_path = None
    if local_dir and os.path.isdir(local_dir):
        for dirpath, _dirnames, filenames in os.walk(local_dir):
            if title in filenames:
                local_path = os.path.join(dirpath, title)
                break
    if local_path is None:
        print("LOCAL_MTIME_MS=UNKNOWN - fisierul nu a fost gasit local")
        print("LOCAL_NEWER_MIN=UNKNOWN")
        return 0

    local_ms = int(os.path.getmtime(local_path) * 1000)
    now_ms = int(time.time() * 1000)
    print("LOCAL_MTIME_MS=" + str(local_ms))
    print("LOCAL_PATH=" + safe(local_path, 400))
    print("CLOUD_AGE_DAYS=" + ("%.2f" % ((now_ms - cloud_ms) / 86400000.0)))
    print("LOCAL_NEWER_MIN=" + ("%.1f" % ((local_ms - cloud_ms) / 60000.0)))
    return 0


def main(argv):
    if len(argv) < 2:
        print("USAGE drivefs_probe.py [--pending | --title T | --root-state | --staleness T --folder F --local D]")
        return 3

    if "--root-state" in argv:
        return report_root_state()

    db = find_db()
    if db is None:
        print("ERROR=no DriveFS metadata database found under " + DRIVEFS_ROOT)
        return 3
    try:
        con = connect_ro(db)
        con.execute("SELECT count(*) FROM sqlite_master").fetchone()
    except Exception as exc:  # noqa: BLE001
        print("ERROR=database unreadable: " + str(exc)[:160])
        return 3

    try:
        if "--pending" in argv:
            n = con.execute("SELECT count(*) FROM operations").fetchone()[0]
            print("PENDING_OPERATIONS=" + str(n))
            print("DB=" + db)
            return 0

        if "--staleness" in argv:
            sidx = argv.index("--staleness")
            if sidx + 1 >= len(argv):
                print("ERROR=--staleness needs a title")
                return 3
            folder = ""
            local = ""
            if "--folder" in argv:
                folder = argv[argv.index("--folder") + 1]
            if "--local" in argv:
                local = argv[argv.index("--local") + 1]
            if not folder:
                print("ERROR=--staleness needs --folder")
                return 3
            return report_staleness(con, argv[sidx + 1], folder, local)

        if "--title" in argv:
            idx = argv.index("--title")
            if idx + 1 >= len(argv):
                print("ERROR=--title needs a value")
                return 3
            title = argv[idx + 1]
            rows = con.execute(
                "SELECT " + ITEM_COLS + " FROM items WHERE local_title = ? LIMIT 20",
                (title,),
            ).fetchall()
            print("LOOKUP=title")
            print("NEEDLE=" + safe(title, 400))
            print("FOUND=" + str(len(rows)))
            print_items(con, rows)
            return 0 if rows else 2

        if "--newest" in argv:
            idx = argv.index("--newest")
            if idx + 1 >= len(argv):
                print("ERROR=--newest needs a value")
                return 3
            folder = argv[idx + 1]
            # Everything under that folder, newest first. The recursive CTE
            # walks stable_parents, which is the real parent relation.
            rows = con.execute(
                "WITH RECURSIVE d(stable_id) AS ("
                "  SELECT stable_id FROM items WHERE local_title = ?"
                "  UNION"
                "  SELECT p.item_stable_id FROM stable_parents p JOIN d"
                "    ON p.parent_stable_id = d.stable_id"
                ") SELECT i.local_title, i.modified_date, i.file_size, i.id"
                " FROM items i JOIN d ON i.stable_id = d.stable_id"
                " WHERE i.is_folder = 0 ORDER BY i.modified_date DESC LIMIT 8",
                (folder,),
            ).fetchall()
            print("LOOKUP=newest")
            print("FOLDER=" + safe(folder, 300))
            print("FOUND=" + str(len(rows)))
            for r in rows:
                print(
                    "NEWEST title=%s modified=%s size=%s cloud_id=%s"
                    % (safe(r[0], 110), r[1], r[2], safe(r[3], 60))
                )
            return 0 if rows else 2

        print("ERROR=unknown argument")
        return 3
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
