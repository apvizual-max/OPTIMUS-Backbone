# 08 — STAGE 8: RISK, CONTAINMENT, QUARANTINE

**You delegate risk when the change could destroy something you cannot recreate.
Delegating it means building the containers first — not asking permission and
hoping.**

---

## Why this is its own stage

Because on the worst night of the worked example — when a change I had applied
without permission returned **zero bytes** from the API — the reason recovery took
four minutes instead of four hours was not skill. It was that three folders already
existed, and the last one was proven to restore.

If you build containment during the happy path, you get it for free when things go
wrong. If you build it in the panic, you build it badly.

---

## The three containers

### BACKUP — a verified copy of what you are about to touch

Not a copy. A **verified** one. The worked example's backup proves itself three ways
on every run:

1. **Every file hashed** (SHA-256) into a manifest, so a restore can be checked.
2. **A sample re-read from disk** and compared — because hashing the file you just
   wrote in memory proves nothing about the file on disk. A script in the worked
   example once spot-checked by hashing the *copied* file and comparing it to a hash
   taken *from that same copied file*. It passed the entire time while 76 files
   were silently missing from the archive. **A check that reads the same object
   twice is not a check.**
3. **Links handled by kind, not by truthiness.** 76 hard-linked files were being
   misclassified as junctions and dropped from the archive, because
   `if ($item.LinkType)` is true for a hard link as well as a junction. The
   manifest recorded them as "recreated as a junction" — an omission *and* a false
   record, which is worse.

### CONTAINMENT — a folder that isolates the blast radius

The backup must not be able to damage what it is copying, and a backup that lives
*inside* what it is copying will recurse into itself forever without an explicit
exclusion. Beyond that, containment is about the *work*: a branch, a folder, a
sandbox — somewhere a broken experiment cannot reach production.

The rule from the worked example, learned by losing a 31-container swarm once:

> **Never** `docker container prune -a`. **Never** `docker rm -f` a named fleet.
> **Never** `--remove-orphans` against a project that owns anything you did not
> create. Write these into the specification as prohibitions, so the rule survives
> your own forgetfulness at 2 a.m.

### QUARANTINE — where the backups live, proven restorable

In the worked example:

```
FULL_BACKUP_2026-10-04_QUARANTINE/
├── BACKUP-MANIFEST.json      every file, hashed; links with their targets
├── <the entire project tree>
└── _DOCS/                    everything needed to rebuild from zero
    ├── 00_REBUILD_FROM_SCRATCH.md
    ├── 02_DEPENDENCIES.md    versions measured, not remembered
    ├── 05_POSTMORTEMS.md     every defect, with the measurement that found it
    └── 03_TREES/             logic · process · strategic · file
```

**"Quarantine" is a discipline, not a folder name.** The requirements are:

- **Separate from the live tree**, so a disaster in one is not a disaster in both.
- **Proven restorable** — not merely *created*. A restore point nobody has restored
  is a hypothesis.
- **Self-describing** — a stranger must be able to rebuild from it with no context
  and no access to you. That is the entire test.
- **Never nested.** A backup containing a backup doubles the size and archives a
  stale earlier run inside the current truth.
- **Refreshed at deliberate checkpoints**, not after every change. Copying 30 MB
  repeatedly is itself a load on the system being protected.

---

## When to delegate risk

You are about to do something you cannot undo, to something you did not create, and
the failure is invisible until it is expensive. Stop. Build the containers, then
ask.

Three questions before you touch anything load-bearing:

1. **If this is wrong, what exactly is gone, and can I get it back?**
2. **Does a verified copy exist *right now*, not one I intend to make?**
3. **Who is allowed to decide this?**

If (2) is not currently true, that is the work. Not the permission.

---

## The handover document

Risk delegation is not finished when the restore point exists. It is finished when
someone can use it.

The worked example's quarantine carries, as standard:

| Document | Answers |
|---|---|
| `00_REBUILD_FROM_SCRATCH.md` | I know nothing. What is this and how do I build it? |
| `02_DEPENDENCIES.md` | What must I install, at which versions? |
| `05_POSTMORTEMS.md` | What has already gone wrong here, and how was it caught? |
| `03_TREES/*` | What does this system do, and what does what depend on? |
| `BACKUP-MANIFEST.json` | Is what I have actually what I think I have? |

And one line above all of them, the test:

> **A stranger must be able to rebuild this from the folder alone. If they cannot,
> the handover is not finished — it is merely written.**
