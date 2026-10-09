"""Jenis galat OREKI."""


class GalatOreki(Exception):
    """Dasar semua galat OREKI."""


class GalatSintaks(GalatOreki):
    """Pertanyaan tidak bisa dibaca."""


class GalatSatuan(GalatOreki):
    """Satuan atau angka tidak dikenal."""


class GalatDimensi(GalatOreki):
    """Dimensi tidak cocok: rumus atau data ditolak."""


class GalatMatematika(GalatOreki):
    """Operasi tidak punya solusi nyata (bagi nol, akar negatif)."""
