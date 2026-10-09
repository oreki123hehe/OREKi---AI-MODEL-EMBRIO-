"""Hukum larangan: menjawab "apakah ini bisa?" dengan menyebut hukumnya.

periksa(fakta) mengembalikan None (tidak relevan) atau (status, alasan) dengan
status 'TIDAK', 'BELUM TAHU', atau 'LOLOS' (hukum ini tidak melarang).
"""
from .hukum import KONSTANTA
from .satuan import format_besaran


class Larangan:
    def __init__(self, id, nama, hukum, syarat, kepercayaan, periksa):
        self.id = id
        self.nama = nama
        self.hukum = hukum
        self.syarat = syarat
        self.kepercayaan = kepercayaan
        self.periksa = periksa


def _periksa_cahaya(f):
    if "v" not in f:
        return None
    v, c = f["v"], KONSTANTA["c"]
    if abs(v) < c:
        return ("LOLOS", [f"v = {format_besaran(v)} < c: batas cahaya tidak dilewati"])
    if "m" not in f:
        return ("BELUM TAHU", [
            "v >= c, tetapi massa tidak dinyatakan",
            "benda tanpa massa (cahaya) bergerak tepat pada c, jadi tidak otomatis dilarang"])
    if f["m"].nilai > 0:
        return ("TIDAK", [
            "energi yang dibutuhkan menuju tak hingga saat v mendekati c",
            "energi tak hingga tidak tersedia",
            "kesimpulan: v >= c tidak tercapai oleh benda bermassa"])
    return ("BELUM TAHU", ["massa nol atau negatif: di luar cakupan basis hukum saat ini"])


def _periksa_energi(f):
    if "E_masuk" not in f or "E_keluar" not in f:
        return None
    sistem = f.get("sistem")
    if sistem is None:
        return ("BELUM TAHU", [
            "status sistem tidak dinyatakan (tambahkan: sistem = tertutup)",
            "kekekalan energi hanya mutlak pada sistem tertutup"])
    if str(sistem).lower() != "tertutup":
        return ("BELUM TAHU", ["sistem tidak tertutup: energi bisa masuk dari luar"])
    if f["E_keluar"] > f["E_masuk"]:
        return ("TIDAK", [
            f"energi keluar ({format_besaran(f['E_keluar'])}) > energi masuk "
            f"({format_besaran(f['E_masuk'])})",
            "pada sistem tertutup energi tidak bisa tercipta"])
    return ("LOLOS", ["energi keluar <= energi masuk: kekekalan energi tidak dilanggar"])


LARANGAN = [
    Larangan("batas_cahaya", "Batas kecepatan cahaya",
             "relativitas khusus (batas kecepatan c)",
             "kerangka inersia; benda bermassa",
             "tinggi (hukum teruji luas)", _periksa_cahaya),
    Larangan("kekekalan_energi", "Kekekalan energi",
             "kekekalan energi", "sistem tertutup",
             "tinggi (hukum teruji luas)", _periksa_energi),
]
