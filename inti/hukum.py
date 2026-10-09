"""Basis hukum v0.1: kinematika dan dinamika Newton.

Setiap hukum membawa rumus, penyelesai untuk tiap variabel, syarat berlaku,
dan fungsi batas yang menolak pemakaian di luar rentang berlakunya.
Konsistensi dimensi setiap penyelesai diperiksa otomatis (cek_konsistensi).
"""
from fractions import Fraction

from .galat import GalatDimensi
from .satuan import Besaran, dimensi, hanya_dimensi

SETENGAH = Fraction(1, 2)
AKAR = Fraction(1, 2)

JENIS = {
    "massa": dimensi(1, 0, 0),
    "panjang": dimensi(0, 1, 0),
    "waktu": dimensi(0, 0, 1),
    "kecepatan": dimensi(0, 1, -1),
    "percepatan": dimensi(0, 1, -2),
    "gaya": dimensi(1, 1, -2),
    "momentum": dimensi(1, 1, -1),
    "energi": dimensi(1, 2, -2),
    "daya": dimensi(1, 2, -3),
    "tekanan": dimensi(1, -1, -2),
    "luas": dimensi(0, 2, 0),
    "volume": dimensi(0, 3, 0),
    "rapat_massa": dimensi(1, -3, 0),
}

SIMBOL = {
    "F": "gaya", "m": "massa", "a": "percepatan", "p": "momentum",
    "v": "kecepatan", "v0": "kecepatan", "dv": "kecepatan",
    "s": "panjang", "h": "panjang", "r": "panjang", "t": "waktu",
    "Ek": "energi", "Ep": "energi", "W": "energi", "P": "daya",
    "g": "percepatan", "m1": "massa", "m2": "massa",
    "Pt": "tekanan", "A": "luas", "rho": "rapat_massa", "V": "volume",
    "E_masuk": "energi", "E_keluar": "energi",
}

KONSTANTA = {
    "c": Besaran(299792458, dimensi(0, 1, -1)),
    "g": Besaran(Fraction("9.80665"), dimensi(0, 1, -2)),
    "G": Besaran(Fraction("6.6743e-11"), dimensi(-1, 3, -2)),
}


def dim_simbol(sim):
    return JENIS[SIMBOL[sim]]


class Hukum:
    def __init__(self, id, nama, rumus, variabel, selesaikan, syarat,
                 bawaan=(), konstanta=(), batas=None):
        self.id = id
        self.nama = nama
        self.rumus = rumus
        self.variabel = tuple(variabel)
        self.selesaikan = selesaikan      # simbol -> fungsi(dict besaran)
        self.syarat = syarat
        self.bawaan = tuple(bawaan)       # simbol yang boleh diisi konstanta
        self.konstanta = tuple(konstanta)  # konstanta tetap yang dipakai rumus
        self.batas = batas

    def bahan(self, diketahui, target):
        """Nilai yang dibutuhkan untuk mencari target, atau None bila kurang."""
        v = {}
        for s in self.variabel:
            if s == target:
                continue
            if s in diketahui:
                v[s] = diketahui[s]
            elif s in self.bawaan:
                v[s] = KONSTANTA[s]
            else:
                return None
        for k in self.konstanta:
            v[k] = KONSTANTA[k]
        return v

    def periksa_batas(self, diketahui):
        """Daftar pelanggaran batas berlaku (kosong = boleh dipakai)."""
        return self.batas(diketahui) if self.batas else []


def _batas_kecepatan(d):
    out = []
    ambang = KONSTANTA["c"] * Fraction(1, 10)
    for sim in ("v", "v0", "dv"):
        if sim in d and abs(d[sim]) > ambang:
            out.append(f"{sim} > 0,1 c: pendekatan Newton tidak akurat "
                       "(butuh relativitas, belum ada di basis)")
    return out


def _batas_glb(d):
    out = _batas_kecepatan(d)
    a = d.get("a")
    if a is not None and a.nilai != 0:
        out.append("GLB hanya berlaku bila percepatan nol (a = 0 harus dinyatakan)")
    return out


BASIS = [
    Hukum("newton2", "Hukum II Newton", "F = m * a", ("F", "m", "a"),
          {"F": lambda v: v["m"] * v["a"],
           "m": lambda v: v["F"] / v["a"],
           "a": lambda v: v["F"] / v["m"]},
          "kerangka acuan inersia; massa konstan; kecepatan jauh di bawah c",
          batas=_batas_kecepatan),
    Hukum("momentum", "Definisi momentum", "p = m * v", ("p", "m", "v"),
          {"p": lambda v: v["m"] * v["v"],
           "m": lambda v: v["p"] / v["v"],
           "v": lambda v: v["p"] / v["m"]},
          "kecepatan jauh di bawah c", batas=_batas_kecepatan),
    Hukum("impuls", "Impuls = perubahan momentum", "F * t = m * dv",
          ("F", "t", "m", "dv"),
          {"F": lambda v: v["m"] * v["dv"] / v["t"],
           "t": lambda v: v["m"] * v["dv"] / v["F"],
           "m": lambda v: v["F"] * v["t"] / v["dv"],
           "dv": lambda v: v["F"] * v["t"] / v["m"]},
          "gaya konstan; massa konstan; kecepatan jauh di bawah c",
          batas=_batas_kecepatan),
    Hukum("percepatan_rata", "Percepatan rata-rata", "a = dv / t",
          ("a", "dv", "t"),
          {"a": lambda v: v["dv"] / v["t"],
           "dv": lambda v: v["a"] * v["t"],
           "t": lambda v: v["dv"] / v["a"]},
          "percepatan konstan pada selang waktu t", batas=_batas_kecepatan),
    Hukum("glb", "Gerak lurus beraturan", "s = v * t", ("s", "v", "t", "a"),
          {"s": lambda v: v["v"] * v["t"],
           "v": lambda v: v["s"] / v["t"],
           "t": lambda v: v["s"] / v["v"]},
          "percepatan nol (a = 0 harus dinyatakan); lintasan lurus",
          batas=_batas_glb),
    Hukum("glbb_v", "GLBB: kecepatan", "v = v0 + a * t", ("v", "v0", "a", "t"),
          {"v": lambda v: v["v0"] + v["a"] * v["t"],
           "v0": lambda v: v["v"] - v["a"] * v["t"],
           "a": lambda v: (v["v"] - v["v0"]) / v["t"],
           "t": lambda v: (v["v"] - v["v0"]) / v["a"]},
          "percepatan konstan; lintasan lurus", batas=_batas_kecepatan),
    Hukum("glbb_s", "GLBB: posisi", "s = v0 * t + 0,5 * a * t^2",
          ("s", "v0", "a", "t"),
          {"s": lambda v: v["v0"] * v["t"] + SETENGAH * v["a"] * v["t"] ** 2,
           "v0": lambda v: (v["s"] - SETENGAH * v["a"] * v["t"] ** 2) / v["t"],
           "a": lambda v: 2 * (v["s"] - v["v0"] * v["t"]) / v["t"] ** 2},
          "percepatan konstan; lintasan lurus (t tidak bisa dicari: kuadratik)",
          batas=_batas_kecepatan),
    Hukum("glbb_v2", "GLBB: tanpa waktu", "v^2 = v0^2 + 2 * a * s",
          ("v", "v0", "a", "s"),
          {"v": lambda v: (v["v0"] ** 2 + 2 * v["a"] * v["s"]) ** AKAR,
           "v0": lambda v: (v["v"] ** 2 - 2 * v["a"] * v["s"]) ** AKAR,
           "a": lambda v: (v["v"] ** 2 - v["v0"] ** 2) / (2 * v["s"]),
           "s": lambda v: (v["v"] ** 2 - v["v0"] ** 2) / (2 * v["a"])},
          "percepatan konstan; lintasan lurus; akar diambil nilai tak-negatif",
          batas=_batas_kecepatan),
    Hukum("ek", "Energi kinetik", "Ek = 0,5 * m * v^2", ("Ek", "m", "v"),
          {"Ek": lambda v: SETENGAH * v["m"] * v["v"] ** 2,
           "m": lambda v: 2 * v["Ek"] / v["v"] ** 2,
           "v": lambda v: (2 * v["Ek"] / v["m"]) ** AKAR},
          "kecepatan jauh di bawah c", batas=_batas_kecepatan),
    Hukum("ep", "Energi potensial gravitasi", "Ep = m * g * h",
          ("Ep", "m", "g", "h"),
          {"Ep": lambda v: v["m"] * v["g"] * v["h"],
           "m": lambda v: v["Ep"] / (v["g"] * v["h"]),
           "h": lambda v: v["Ep"] / (v["m"] * v["g"]),
           "g": lambda v: v["Ep"] / (v["m"] * v["h"])},
          "medan gravitasi seragam (dekat permukaan); g bawaan 9,80665 m/s2",
          bawaan=("g",)),
    Hukum("usaha", "Usaha", "W = F * s", ("W", "F", "s"),
          {"W": lambda v: v["F"] * v["s"],
           "F": lambda v: v["W"] / v["s"],
           "s": lambda v: v["W"] / v["F"]},
          "gaya konstan, searah perpindahan"),
    Hukum("daya", "Daya rata-rata", "P = W / t", ("P", "W", "t"),
          {"P": lambda v: v["W"] / v["t"],
           "W": lambda v: v["P"] * v["t"],
           "t": lambda v: v["W"] / v["P"]},
          "rata-rata pada selang waktu t"),
    Hukum("gravitasi", "Gravitasi Newton", "F = G * m1 * m2 / r^2",
          ("F", "m1", "m2", "r"),
          {"F": lambda v: v["G"] * v["m1"] * v["m2"] / v["r"] ** 2,
           "m1": lambda v: v["F"] * v["r"] ** 2 / (v["G"] * v["m2"]),
           "m2": lambda v: v["F"] * v["r"] ** 2 / (v["G"] * v["m1"]),
           "r": lambda v: (v["G"] * v["m1"] * v["m2"] / v["F"]) ** AKAR},
          "medan lemah, benda dianggap titik; G = 6,6743e-11 N.m2/kg2",
          konstanta=("G",), batas=_batas_kecepatan),
    Hukum("tekanan", "Tekanan", "Pt = F / A", ("Pt", "F", "A"),
          {"Pt": lambda v: v["F"] / v["A"],
           "F": lambda v: v["Pt"] * v["A"],
           "A": lambda v: v["F"] / v["Pt"]},
          "gaya tegak lurus permukaan, terbagi merata"),
    Hukum("rapat_massa", "Rapat massa", "rho = m / V", ("rho", "m", "V"),
          {"rho": lambda v: v["m"] / v["V"],
           "m": lambda v: v["rho"] * v["V"],
           "V": lambda v: v["m"] / v["rho"]},
          "zat homogen"),
]


def cek_konsistensi():
    """Setiap penyelesai harus menghasilkan dimensi jenis simbol targetnya.

    Mengembalikan daftar masalah (kosong = semua hukum konsisten).
    """
    masalah = []
    with hanya_dimensi():
        for h in BASIS:
            for s in h.variabel:
                if s not in SIMBOL:
                    masalah.append(f"{h.id}: simbol '{s}' tidak ada di tabel SIMBOL")
            for target, fungsi in h.selesaikan.items():
                v = {s: Besaran(4, dim_simbol(s))
                     for s in h.variabel if s != target}
                for k in h.konstanta:
                    v[k] = KONSTANTA[k]
                try:
                    hasil = fungsi(v)
                except GalatDimensi as e:
                    masalah.append(f"{h.id}.{target}: {e}")
                    continue
                if hasil.dim != dim_simbol(target):
                    masalah.append(f"{h.id}.{target}: dimensi hasil tidak sesuai jenis "
                                   f"'{SIMBOL[target]}'")
    return masalah
