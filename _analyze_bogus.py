"""Analysa arborelui 'fals' din origin/main.

origin/main contine un director la nivel de radacina cu numele literal
C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME - o cale absoluta
Windows comitata ca intrare de arbore. Git refuza ':' intr-o componenta de
nume, deci read-tree / checkout esueaza si nicio clona pe Windows nu se poate
materializa.

Scriptul raspunde la intrebarea esentiala: fisierele din arborele fals sunt
duplicate ale celor de la calea reala, sau contin continut unic?
"""
import subprocess
import sys

PREFIX = b"C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME"


def g(*args):
    return subprocess.run(["git"] + list(args), capture_output=True).stdout


def main():
    raw = g("ls-tree", "-r", "-z", "origin/main")
    entries = [e for e in raw.split(b"\0") if e]
    bogus = {}
    real = {}
    for e in entries:
        meta, name = e.split(b"\t", 1)
        mode, typ, sha = meta.split(b" ")
        if name.startswith(PREFIX + b"/"):
            bogus[name[len(PREFIX) + 1:]] = (mode.decode(), sha.decode())
        else:
            real[name] = (mode.decode(), sha.decode())

    print("intrari_in_arborele_fals:", len(bogus))
    print("intrari_la_calea_reala:", len(real))

    identical = 0
    different = []
    only_bogus = []
    for name, (mode, sha) in sorted(bogus.items()):
        other = real.get(name)
        if other is None:
            only_bogus.append(name)
        elif other[1] == sha:
            identical += 1
        else:
            different.append((name, sha[:10], other[1][:10]))

    print("identice cu calea reala:", identical)
    print("diferite:", len(different))
    for d in different:
        print("   DIF", d[0], "fals=", d[1], "real=", d[2])
    print("exista DOAR in arborele fals:", len(only_bogus))
    for name in only_bogus:
        print("   DOAR", name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
