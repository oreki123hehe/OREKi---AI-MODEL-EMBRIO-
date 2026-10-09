"""Mesin penalaran: pertanyaan terstruktur -> jawaban beralasan dan teraudit."""
from dataclasses import dataclass, field

from .baca import baca
from .galat import GalatDimensi, GalatMatematika, GalatOreki, GalatSintaks
from .hukum import BASIS, SIMBOL, dim_simbol
from .larangan import LARANGAN
from .satuan import Besaran, format_besaran, nama_dimensi

KEDALAMAN_MAKS = 3  # jumlah hukum perantara maksimum dalam satu rantai


@dataclass
class Langkah:
    hukum: object
    target: str
    bahan: dict
    nilai: Besaran


@dataclass
class Jawaban:
    status: str
    pertanyaan: str = ""
    target: str = ""
    hasil: Besaran = None
    fakta: dict = field(default_factory=dict)
    langkah: list = field(default_factory=list)
    hukum: list = field(default_factory=list)
    alasan: list = field(default_factory=list)
    peringatan: list = field(default_factory=list)
    kepercayaan: str = ""


def _catat(daftar, teks):
    if teks not in daftar:
        daftar.append(teks)


def _dekat(a, b):
    a, b = float(a), float(b)
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def _validasi_fakta(fakta):
    for sim, nilai in fakta.items():
        if sim == "sistem":
            continue
        if sim not in SIMBOL:
            raise GalatSintaks(f"simbol tidak dikenal: '{sim}'")
        if nilai.dim != dim_simbol(sim):
            raise GalatDimensi(
                f"{sim} harus berjenis {SIMBOL[sim]} "
                f"({nama_dimensi(dim_simbol(sim))}), tetapi diberi "
                f"{format_besaran(nilai)} ({nama_dimensi(nilai.dim)})")


def _langsung(target, diketahui, catatan):
    """Semua hukum yang bisa langsung menghitung target dari data yang ada."""
    hasil = []
    for h in BASIS:
        if target not in h.selesaikan:
            continue
        bahan = h.bahan(diketahui, target)
        if bahan is None:
            continue
        pelanggaran = h.periksa_batas({**diketahui, **bahan})
        if pelanggaran:
            for p in pelanggaran:
                _catat(catatan, f"{h.nama}: {p}")
            continue
        try:
            nilai = h.selesaikan[target](bahan)
        except GalatMatematika as e:
            _catat(catatan, f"{h.nama}: {e}")
            continue
        hasil.append((h, bahan, nilai))
    return hasil


def _turunkan(target, diketahui, sisa, tumpukan, catatan):
    langsung = _langsung(target, diketahui, catatan)
    if langsung:
        h, bahan, nilai = langsung[0]
        peringatan = []
        for h2, _, n2 in langsung[1:]:
            if n2.dim == nilai.dim and not _dekat(n2.nilai, nilai.nilai):
                peringatan.append(
                    f"{h2.nama} memberi {target} = {format_besaran(n2)}, berbeda "
                    f"dari {format_besaran(nilai)}: data masukan mungkin tidak konsisten")
        return nilai, [Langkah(h, target, bahan, nilai)], peringatan
    if sisa == 0:
        return None
    for h in BASIS:
        if target not in h.selesaikan:
            continue
        hilang = [s for s in h.variabel
                  if s != target and s not in diketahui and s not in h.bawaan]
        if not hilang or any(s in tumpukan for s in hilang):
            continue
        lokal, langkah, ok = dict(diketahui), [], True
        for s in hilang:
            r = _turunkan(s, lokal, sisa - 1, tumpukan + (target,), catatan)
            if r is None:
                ok = False
                break
            lokal[s] = r[0]
            langkah += r[1]
        if not ok:
            continue
        bahan = h.bahan(lokal, target)
        pelanggaran = h.periksa_batas({**lokal, **bahan})
        if pelanggaran:
            for p in pelanggaran:
                _catat(catatan, f"{h.nama}: {p}")
            continue
        try:
            nilai = h.selesaikan[target](bahan)
        except GalatMatematika as e:
            _catat(catatan, f"{h.nama}: {e}")
            continue
        return nilai, langkah + [Langkah(h, target, bahan, nilai)], []
    return None


def _cari(target, fakta, catatan):
    for kedalaman in range(KEDALAMAN_MAKS + 1):  # rantai terpendek dulu
        r = _turunkan(target, fakta, kedalaman, (), catatan)
        if r:
            return r
    return None


def _hitung(p):
    _validasi_fakta(p.fakta)
    if p.target not in SIMBOL:
        raise GalatSintaks(f"simbol tidak dikenal: '{p.target}'")
    if p.target in p.fakta:
        raise GalatSintaks(f"{p.target} sudah diberikan, tidak perlu dihitung")
    j = Jawaban("HASIL", p.teks, p.target, fakta=p.fakta)
    catatan = []
    r = _cari(p.target, p.fakta, catatan)
    if r is None:
        j.status = "BELUM TAHU"
        if catatan:
            j.alasan = catatan + [
                "tidak ada hukum lain di basis yang bisa dipakai di dalam batas berlakunya"]
        else:
            j.alasan = [
                f"tidak ditemukan rantai hukum dari data ke {p.target} "
                f"(perantara maksimum {KEDALAMAN_MAKS}): data kurang atau hukumnya "
                "belum ada di basis"]
        j.kepercayaan = "tidak menebak"
        return j
    nilai, langkah, peringatan = r
    if nilai.dim != dim_simbol(p.target):
        raise GalatDimensi(f"hasil {p.target} tidak berdimensi {SIMBOL[p.target]}")
    j.hasil, j.langkah, j.peringatan = nilai, langkah, peringatan
    for l in langkah:
        baris = f"{l.hukum.nama} (berlaku: {l.hukum.syarat})"
        if baris not in j.hukum:
            j.hukum.append(baris)
    j.kepercayaan = ("tinggi (hukum teruji luas), sah selama syarat hukum terpenuhi"
                     if len(langkah) == 1 else
                     f"tinggi per hukum; rantai {len(langkah)} hukum, "
                     "sah selama semua syarat terpenuhi")
    return j


def _bisa(p):
    _validasi_fakta(p.fakta)
    j = Jawaban("", p.teks, fakta=p.fakta)
    temuan = [(l, *r) for l in LARANGAN if (r := l.periksa(p.fakta))]
    melanggar = [t for t in temuan if t[1] == "TIDAK"]
    ragu = [t for t in temuan if t[1] == "BELUM TAHU"]
    if melanggar:
        j.status = "TIDAK"
        for l, _, alasan in melanggar:
            j.hukum.append(f"{l.hukum} (berlaku: {l.syarat})")
            j.alasan += alasan
        j.kepercayaan = melanggar[0][0].kepercayaan
    elif ragu:
        j.status = "BELUM TAHU"
        for l, _, alasan in ragu:
            j.hukum.append(f"{l.hukum} (berlaku: {l.syarat})")
            j.alasan += alasan
        j.kepercayaan = "tidak menebak"
    elif temuan:
        j.status = "DIIZINKAN HUKUM"
        for l, _, alasan in temuan:
            j.hukum.append(f"{l.hukum} (berlaku: {l.syarat})")
            j.alasan += alasan
        j.alasan.append(
            "kelayakan rekayasa (material, energi, biaya) belum dinilai: "
            "BISA SEKARANG / BISA NANTI butuh lapis 2 dan 3 yang belum ada di v0.1")
        j.kepercayaan = "hanya lapis 1 (hukum tidak melarang)"
    else:
        j.status = "BELUM TAHU"
        j.alasan = ["tidak ada hukum dalam basis yang menjawab pertanyaan ini"]
        j.kepercayaan = "tidak menebak"
    return j


def jawab(teks):
    try:
        p = baca(teks)
        return _hitung(p) if p.jenis == "hitung" else _bisa(p)
    except GalatOreki as e:
        return Jawaban("DITOLAK", teks.strip(), alasan=[str(e)])


def _fmt(x):
    return format_besaran(x) if isinstance(x, Besaran) else str(x)


def cetak(j):
    b = [f"tanya : {j.pertanyaan}"]
    n = 0
    if j.fakta:
        n += 1
        tangkap = ", ".join(f"{k} = {_fmt(v)}" for k, v in j.fakta.items())
        b.append(f"{n}. tangkap -> {tangkap}" + (f", dicari {j.target}" if j.target else ""))
    for l in j.langkah:
        n += 1
        b.append(f"{n}. cocokkan -> {l.hukum.rumus}  [{l.hukum.nama}]")
        n += 1
        b.append(f"{n}. cek dimensi -> {l.target}: {nama_dimensi(l.nilai.dim)} "
                 f"= {SIMBOL[l.target]}, sesuai")
        n += 1
        b.append(f"{n}. hitung -> {l.target} = {format_besaran(l.nilai)}")
    b.append("")
    if j.status == "HASIL":
        b.append(f"JAWABAN : {j.target} = {format_besaran(j.hasil)}")
    else:
        b.append(f"JAWABAN : {j.status}")
    for h in j.hukum:
        b.append(f"HUKUM : {h}")
    if len(j.alasan) == 1:
        b.append(f"ALASAN : {j.alasan[0]}")
    elif j.alasan:
        b.append("ALASAN :")
        b += [f"  {i}. {a}" for i, a in enumerate(j.alasan, 1)]
    for w in j.peringatan:
        b.append(f"PERINGATAN : {w}")
    if j.kepercayaan:
        b.append(f"KEPERCAYAAN : {j.kepercayaan}")
    return "\n".join(b)
