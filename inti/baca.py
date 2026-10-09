"""Pembaca pertanyaan terstruktur v0.1 (jembatan sebelum bahasa OREKI penuh).

  hitung F ; m = 2 kg ; a = 3 m/s2
  bisa v = 1,5 c ; m = 1 kg
  bisa E_masuk = 100 J ; E_keluar = 120 J ; sistem = tertutup

Desimal memakai koma; titik dicadangkan sebagai pemisah pipeline bahasa nanti.
"""
from dataclasses import dataclass, field

from .galat import GalatSintaks
from .satuan import parse_besaran


@dataclass
class Pertanyaan:
    jenis: str
    target: str
    fakta: dict = field(default_factory=dict)
    teks: str = ""


def baca(teks):
    bagian = [b.strip() for b in teks.split(";") if b.strip()]
    if not bagian:
        raise GalatSintaks("pertanyaan kosong")
    kata, _, sisa = bagian[0].partition(" ")
    kata, sisa = kata.lower(), sisa.strip()
    segmen, target = bagian[1:], ""
    if kata == "hitung":
        if not sisa or " " in sisa or "=" in sisa:
            raise GalatSintaks("pakai: hitung <simbol> ; nama = nilai satuan ; ...")
        target = sisa
    elif kata == "bisa":
        if sisa:
            segmen = [sisa] + segmen
    else:
        raise GalatSintaks(f"kata kunci tidak dikenal: '{kata}' (pakai: hitung / bisa)")
    fakta = {}
    for s in segmen:
        nama, tanda, nilai = (x.strip() for x in s.partition("="))
        if not tanda or not nama or not nilai:
            raise GalatSintaks(f"fakta tidak valid: '{s}' (pakai: nama = nilai satuan)")
        if nama in fakta:
            raise GalatSintaks(f"'{nama}' diberikan dua kali")
        fakta[nama] = nilai if nama == "sistem" else parse_besaran(nilai)
    return Pertanyaan(kata, target, fakta, teks.strip())
