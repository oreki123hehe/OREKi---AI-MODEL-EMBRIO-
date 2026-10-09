#!/usr/bin/env python3
"""OREKI v0.1: mesin penalaran berbasis hukum alam.

  python oreki.py tanya "hitung F ; m = 2 kg ; a = 3 m/s2"
  python oreki.py tanya "bisa v = 1,5 c ; m = 1 kg"
  python oreki.py chat | hukum | cek | uji | demo
"""
import os
import sys

from inti.hukum import BASIS, cek_konsistensi
from inti.larangan import LARANGAN
from inti.mesin import cetak, jawab

CONTOH = [
    "hitung F ; m = 2 kg ; a = 3 m/s2",
    "hitung Ek ; F = 10 N ; m = 2 kg ; t = 3 s ; v0 = 0 m/s",
    "hitung v ; s = 100 m ; t = 20 s ; a = 0 m/s2",
    "hitung v ; s = 100 m ; t = 20 s",
    "bisa v = 1,5 c ; m = 1 kg",
    "bisa v = 0,5 c ; m = 1 kg",
    "bisa E_masuk = 100 J ; E_keluar = 120 J ; sistem = tertutup",
    "hitung F ; m = 2 s ; a = 3 m/s2",
]


def tanya(argv):
    if not argv:
        print('Pakai: python oreki.py tanya "hitung F ; m = 2 kg ; a = 3 m/s2"')
        return 1
    print(cetak(jawab(" ".join(argv))))
    return 0


def chat():
    print("OREKI v0.1. Ketik pertanyaan terstruktur, kosong untuk keluar.")
    while True:
        try:
            baris = input("oreki> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not baris:
            return 0
        print(cetak(jawab(baris)))
        print()


def hukum():
    print(f"{len(BASIS)} hukum persamaan:")
    for h in BASIS:
        print(f"  {h.rumus:<28} {h.nama}")
        print(f"      berlaku: {h.syarat}")
    print(f"\n{len(LARANGAN)} hukum larangan:")
    for l in LARANGAN:
        print(f"  {l.nama}  (berlaku: {l.syarat})")
    return 0


def cek():
    print("Python", sys.version.split()[0])
    masalah = cek_konsistensi()
    if masalah:
        print("[gagal] konsistensi dimensi hukum:")
        for m in masalah:
            print("  -", m)
        return 1
    print(f"[ok]    {len(BASIS)} hukum konsisten dimensinya")
    return 0


def uji():
    import unittest
    akar = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(akar, "tes")
    suite = unittest.defaultTestLoader.discover(folder, top_level_dir=folder)
    hasil = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if hasil.wasSuccessful() else 1


def demo():
    for q in CONTOH:
        print(cetak(jawab(q)))
        print("-" * 60)
    return 0


PERINTAH = {"chat": chat, "hukum": hukum, "cek": cek, "uji": uji, "demo": demo}

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "tanya":
        sys.exit(tanya(sys.argv[2:]))
    if len(sys.argv) >= 2 and sys.argv[1] in PERINTAH:
        sys.exit(PERINTAH[sys.argv[1]]())
    print(__doc__)
    sys.exit(1)
