#!/usr/bin/env python3
import sys
from inti import batas

EFISIENSI = 0.3  # asumsi kasar: latih nyata ~30% dari kecepatan puncak matmul


def status():
    print("OREKI AI (Embrio)")
    print(f"Batas parameter : {batas.MAKS_PARAMETER:,}")
    print(f"Batas RAM       : {batas.MAKS_RAM_MB} MB")
    print(f"RAM terpakai    : {batas.rss_anon_mb()} MB ({batas.status_ram()})")


def benchmark():
    try:
        import time
        import torch
    except Exception:
        print("Benchmark dilewati: torch belum bisa dipakai")
        return
    n, iterasi = 512, 30
    a, b = torch.randn(n, n), torch.randn(n, n)
    for _ in range(3):  # pemanasan
        a @ b
    t0 = time.perf_counter()
    for _ in range(iterasi):
        a @ b
    dt = time.perf_counter() - t0
    gflops = 2 * n ** 3 * iterasi / dt / 1e9
    print(f"Benchmark matmul : {gflops:.1f} GFLOPS ({torch.get_num_threads()} thread)")
    efektif = gflops * 1e9 * EFISIENSI
    for nama, param, token in (("tahap 1", 2e6, 40e6), ("tahap 5", 109e6, 2.2e9)):
        hari = 6 * param * token / efektif / 86400  # FLOP latih ~ 6 x param x token
        print(f"Perkiraan latih {nama}: {hari:,.1f} hari "
              f"(efisiensi {int(EFISIENSI * 100)}%, sangat kasar)")


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
    benchmark()


PERINTAH = {"status": status, "cek": cek}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in PERINTAH:
        print("Pakai: python oreki.py [" + " | ".join(PERINTAH) + "]")
        sys.exit(1)
    PERINTAH[sys.argv[1]]()
