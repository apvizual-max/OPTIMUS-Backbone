"""Repara arborelui 'fals' din origin/main, fara a atinge indexul.

Defect: origin/main contine un director la radacina numit literal
C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME. Git refuza ':' intr-o
componenta de nume, deci `read-tree`, `checkout` si orice clona pe Windows
esueaza. Arborele fals contine 12 intrari:
  - 2 identice cu calea reala
  - 9 snapshoturi mai vechi ale fisierelor de stare runtime
  - 1 fisier care exista DOAR acolo (09_LOGS/scraped/example_com_20261024_060614.json)

Ce face scriptul, in ordine:
  1. salveaza toate cele 12 intrari in quarantine, ca nimic sa nu se piarda
  2. extrage fisierul unic la calea lui reala, in arborele de lucru
  3. construieste un arbore radacina nou, fara directorul fals
  4. creeaza un commit de reparatie, parinte origin/main (istoria ramane liniara)
Nu muta nicio referinta - asta se face separat, dupa ce scriptul raporteaza.
"""
import os
import subprocess
import sys

REPO = r"C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME"
PREFIX = b"C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME"
QUARANTINE = os.path.join(REPO, "13_COMMAND_CENTER", "_QUARANTINE",
                          "abs-path-tree-2026-10-28")


def g(*args, **kw):
    return subprocess.run(["git"] + list(args), capture_output=True, cwd=REPO, **kw)


def main():
    raw = g("ls-tree", "-r", "-z", "origin/main").stdout
    entries = [e for e in raw.split(b"\0") if e]
    bogus, real = {}, {}
    for e in entries:
        meta, name = e.split(b"\t", 1)
        mode, typ, sha = meta.split(b" ")
        if name.startswith(PREFIX + b"/"):
            bogus[name[len(PREFIX) + 1:].decode("utf-8", "surrogateescape")] = (
                mode.decode(), sha.decode())
        else:
            real[name.decode("utf-8", "surrogateescape")] = (mode.decode(), sha.decode())

    print("intrari_fals:", len(bogus), " intrari_reale:", len(real))
    if not bogus:
        print("NIMIC de reparat: arborele fals nu mai exista.")
        return 0

    # ---- 1. salvarea continutului, inainte de orice scriere -------------
    os.makedirs(QUARANTINE, exist_ok=True)
    saved = 0
    for name, (mode, sha) in sorted(bogus.items()):
        dest = os.path.join(QUARANTINE, name.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        blob = g("cat-file", "blob", sha).stdout
        with open(dest, "wb") as fh:
            fh.write(blob)
        saved += 1
    print("salvate in quarantine:", saved, "->", QUARANTINE)

    # ---- 2. fisierul unic, extras la calea lui reala --------------------
    only_bogus = [n for n in bogus if n not in real]
    for name in only_bogus:
        sha = bogus[name][1]
        blob = g("cat-file", "blob", sha).stdout
        dest = os.path.join(REPO, name.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(blob)
        print("extras la calea reala:", name, len(blob), "octeti")

    # ---- 3. arbore radacina nou, fara directorul fals -------------------
    root = g("ls-tree", "-z", "origin/main").stdout
    kept = []
    dropped = 0
    for e in root.split(b"\0"):
        if not e:
            continue
        meta, name = e.split(b"\t", 1)
        if name.startswith(PREFIX):
            dropped += 1
            continue
        kept.append(e)
    print("intrari_radacina pastrate:", len(kept), " eliminate:", dropped)
    proc = subprocess.run(["git", "mktree", "-z"], input=b"\0".join(kept) + b"\0",
                          capture_output=True, cwd=REPO)
    if proc.returncode != 0:
        print("mktree a esuat:", proc.stderr.decode("utf-8", "replace"))
        return 1
    new_tree = proc.stdout.strip().decode()
    print("arbore_nou:", new_tree)

    # ---- 4. commit de reparatie -----------------------------------------
    old = g("rev-parse", "origin/main").stdout.decode().strip()
    msg = ("Repara: elimina directorul cu cale absoluta din radacina\n"
           "\n"
           "origin/main continea intrarea de arbore\n"
           '"C:\\\\Users\\\\apviz\\\\.minimax-agent\\\\projects\\\\SENTINEL_PRIME"\n'
           "ca director de radacina. Git refuza ':' intr-o componenta de nume, deci\n"
           "read-tree, checkout si orice clona pe Windows esueau cu\n"
           "\"error: invalid path\". Defectul a fost introdus de 3b3f9dd\n"
           "(Code Health: Break down monolithic test_brain_and_monitor, PR #14).\n"
           "\n"
           "Cele 12 intrari din arborele fals au fost salvate inainte de reparatie,\n"
           "la 13_COMMAND_CENTER/_QUARANTINE/abs-path-tree-2026-10-28/.\n"
           "Dintre ele, 2 erau identice cu calea reala, 9 erau snapshoturi mai\n"
           "vechi ale fisierelor de stare runtime, iar\n"
           "09_LOGS/scraped/example_com_20261024_060614.json exista DOAR acolo -\n"
           "a fost extras la calea lui reala.\n"
           "\n"
           "Istoria ramane liniara: acest commit are ca parinte origin/main.\n")
    proc = subprocess.run(["git", "commit-tree", new_tree, "-p", old, "-m", msg],
                          capture_output=True, cwd=REPO)
    if proc.returncode != 0:
        print("commit-tree a esuat:", proc.stderr.decode("utf-8", "replace"))
        return 1
    new_commit = proc.stdout.strip().decode()
    print("commit_reparatie:", new_commit)
    print("parinte:", old)
    print("verificare_arbore:", g("ls-tree", new_commit).stdout.count(b"\n"), "intrari la radacina")
    print("INTRODUCE:", new_commit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
