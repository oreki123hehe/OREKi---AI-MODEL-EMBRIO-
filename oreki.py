#!/usr/bin/env python3
import sys
from inti import batas


def status():
    print("OREKI AI (Embrio)")
    print(f"Batas parameter : {batas.MAKS_PARAMETER:,}")
    print(f"Batas RAM       : {batas.MAKS_RAM_MB} MB")
    print(f"RAM terpakai    : {batas.rss_anon_mb()} MB ({batas.status_ram()})")


def cek():
    print("Python", sys.version.split()[0])
    for nama in ("numpy", "torch", "requests", "bs4"):
        try:
            __import__(nama)
            print(f"[ok]     {nama}")
        except ImportError:
            print(f"[belum]  {nama}")


PERINTAH = {"status": status, "cek": cek}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in PERINTAH:
        print("Pakai: python oreki.py [" + " | ".join(PERINTAH) + "]")
        sys.exit(1)
    PERINTAH[sys.argv[1]]()
