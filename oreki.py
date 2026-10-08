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
            modul = __import__(nama)
            versi = getattr(modul, "__version__", "?")
            print(f"[ok]     {nama} {versi}")
        except Exception as e:
            # Tampilkan penyebab asli, bukan hanya "belum"
            print(f"[gagal]  {nama}: {type(e).__name__}: {str(e)[:200]}")


PERINTAH = {"status": status, "cek": cek}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in PERINTAH:
        print("Pakai: python oreki.py [" + " | ".join(PERINTAH) + "]")
        sys.exit(1)
    PERINTAH[sys.argv[1]]()
