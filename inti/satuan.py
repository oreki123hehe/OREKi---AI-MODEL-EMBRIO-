"""Besaran bersatuan: setiap nilai membawa dimensinya (massa, panjang, waktu).

Nilai disimpan sebagai pecahan eksak (Fraction) selama mungkin; akar
menghasilkan float. Menjumlah besaran berbeda dimensi langsung ditolak.
"""
import re
from contextlib import contextmanager
from fractions import Fraction

from .galat import GalatDimensi, GalatMatematika, GalatSatuan


def dimensi(*d):
    """Vektor dimensi (massa, panjang, waktu)."""
    return tuple(Fraction(x) for x in d)


NOL = dimensi(0, 0, 0)
_HANYA_DIMENSI = False


@contextmanager
def hanya_dimensi():
    """Mode pemeriksaan dimensi: nilai tidak penting, akar negatif diabaikan."""
    global _HANYA_DIMENSI
    lama, _HANYA_DIMENSI = _HANYA_DIMENSI, True
    try:
        yield
    finally:
        _HANYA_DIMENSI = lama


class Besaran:
    __slots__ = ("nilai", "dim")
    __hash__ = None

    def __init__(self, nilai, dim=NOL):
        self.nilai = Fraction(nilai) if isinstance(nilai, int) else nilai
        self.dim = dimensi(*dim)

    @staticmethod
    def _ke(x):
        return x if isinstance(x, Besaran) else Besaran(x)

    def _sama(self, lain, aksi):
        if self.dim != lain.dim:
            raise GalatDimensi(
                f"tidak bisa {aksi}: {nama_dimensi(self.dim)} dan "
                f"{nama_dimensi(lain.dim)} berbeda dimensi"
            )

    def __add__(self, lain):
        lain = self._ke(lain)
        self._sama(lain, "menjumlah")
        return Besaran(self.nilai + lain.nilai, self.dim)

    __radd__ = __add__

    def __sub__(self, lain):
        lain = self._ke(lain)
        self._sama(lain, "mengurang")
        return Besaran(self.nilai - lain.nilai, self.dim)

    def __rsub__(self, lain):
        return self._ke(lain) - self

    def __mul__(self, lain):
        lain = self._ke(lain)
        return Besaran(self.nilai * lain.nilai,
                       tuple(a + b for a, b in zip(self.dim, lain.dim)))

    __rmul__ = __mul__

    def __truediv__(self, lain):
        lain = self._ke(lain)
        if lain.nilai == 0:
            raise GalatMatematika("pembagian dengan nol")
        return Besaran(self.nilai / lain.nilai,
                       tuple(a - b for a, b in zip(self.dim, lain.dim)))

    def __rtruediv__(self, lain):
        return self._ke(lain) / self

    def __pow__(self, eks):
        e = Fraction(eks)
        if e.denominator == 1:
            if self.nilai == 0 and e < 0:
                raise GalatMatematika("pembagian dengan nol")
            nilai = self.nilai ** int(e)
        else:
            x = float(self.nilai)
            if x < 0:
                if not _HANYA_DIMENSI:
                    raise GalatMatematika(
                        "akar bilangan negatif: tidak ada solusi nyata")
                x = abs(x)
            nilai = x ** float(e)
        return Besaran(nilai, tuple(d * e for d in self.dim))

    def __neg__(self):
        return Besaran(-self.nilai, self.dim)

    def __abs__(self):
        return Besaran(abs(self.nilai), self.dim)

    def _banding(self, lain):
        lain = self._ke(lain)
        self._sama(lain, "membandingkan")
        return lain

    def __lt__(self, lain):
        return self.nilai < self._banding(lain).nilai

    def __le__(self, lain):
        return self.nilai <= self._banding(lain).nilai

    def __gt__(self, lain):
        return self.nilai > self._banding(lain).nilai

    def __ge__(self, lain):
        return self.nilai >= self._banding(lain).nilai

    def __eq__(self, lain):
        if not isinstance(lain, (Besaran, int, float, Fraction)):
            return NotImplemented
        lain = self._ke(lain)
        return self.dim == lain.dim and self.nilai == lain.nilai

    def __repr__(self):
        return format_besaran(self)

    __str__ = __repr__


# --- tabel satuan ---------------------------------------------------------
_M, _L, _T = dimensi(1, 0, 0), dimensi(0, 1, 0), dimensi(0, 0, 1)
_SATUAN = {
    "kg": (Fraction(1), _M),
    "g": (Fraction(1, 1000), _M),
    "m": (Fraction(1), _L),
    "cm": (Fraction(1, 100), _L),
    "km": (Fraction(1000), _L),
    "s": (Fraction(1), _T),
    "menit": (Fraction(60), _T),
    "jam": (Fraction(3600), _T),
    "N": (Fraction(1), dimensi(1, 1, -2)),
    "J": (Fraction(1), dimensi(1, 2, -2)),
    "kJ": (Fraction(1000), dimensi(1, 2, -2)),
    "W": (Fraction(1), dimensi(1, 2, -3)),
    "Pa": (Fraction(1), dimensi(1, -1, -2)),
    "c": (Fraction(299792458), dimensi(0, 1, -1)),  # kecepatan cahaya
}
_TURUNAN = {
    dimensi(1, 1, -2): "N",
    dimensi(1, 2, -2): "J",
    dimensi(1, 2, -3): "W",
    dimensi(1, -1, -2): "Pa",
}
_DASAR = ("kg", "m", "s")
_RE_ANGKA = re.compile(r"^\s*([-+]?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?)\s*(.*?)\s*$")
_RE_ATOM = re.compile(r"^([A-Za-z]+)(-?\d+)?$")


def parse_satuan(teks):
    """'m/s2' -> (faktor ke satuan dasar, dimensi). Pemisah: * dan /."""
    teks = teks.strip()
    faktor, dim = Fraction(1), NOL
    if not teks:
        return faktor, dim
    for i, grup in enumerate(teks.split("/")):
        tanda = 1 if i == 0 else -1
        for atom in grup.split("*"):
            atom = atom.strip()
            m = _RE_ATOM.match(atom)
            if not m or m.group(1) not in _SATUAN:
                raise GalatSatuan(f"satuan tidak dikenal: '{atom}'")
            f, d = _SATUAN[m.group(1)]
            eks = int(m.group(2) or 1) * tanda
            faktor *= f ** eks
            dim = tuple(a + b * eks for a, b in zip(dim, d))
    return faktor, dim


def parse_besaran(teks):
    """'1,5 m/s2' -> Besaran. Desimal ditulis dengan koma (titik = pemisah)."""
    m = _RE_ANGKA.match(teks)
    if not m:
        raise GalatSatuan(f"bukan besaran: '{teks}' (contoh: 2 kg, 9,8 m/s2)")
    nilai = Fraction(m.group(1).replace(",", "."))
    faktor, dim = parse_satuan(m.group(2))
    return Besaran(nilai * faktor, dim)


def _pangkat(u, e):
    if e == 1:
        return u
    if e.denominator == 1:
        return f"{u}{e.numerator}"
    return f"{u}^({e})"


def nama_satuan(dim):
    """Dimensi -> nama satuan SI, mis. (1,1,-2) -> 'N', (0,1,-2) -> 'm/s2'."""
    dim = dimensi(*dim)
    if dim in _TURUNAN:
        return _TURUNAN[dim]
    atas, bawah = [], []
    for u, e in zip(_DASAR, dim):
        if e == 0:
            continue
        (atas if e > 0 else bawah).append(_pangkat(u, abs(e)))
    if not atas and not bawah:
        return ""
    s = "*".join(atas) or "1"
    if bawah:
        s += "/" + (bawah[0] if len(bawah) == 1 else "(" + "*".join(bawah) + ")")
    return s


def nama_dimensi(dim):
    return nama_satuan(dim) or "tanpa satuan"


def format_nilai(x):
    if isinstance(x, Fraction) and x.denominator == 1:
        return str(x.numerator)
    return f"{float(x):.10g}".replace(".", ",")


def format_besaran(b):
    return f"{format_nilai(b.nilai)} {nama_satuan(b.dim)}".strip()
