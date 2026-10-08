"""Batas terkunci OREKI. Tidak boleh diubah oleh skill atau OREKI sendiri."""

MAKS_PARAMETER = 110_000_000
MAKS_RAM_MB = 3072          # batas keras 3 GB
PERINGATAN_RAM_MB = 2764    # sekitar 2,7 GB


def rss_anon_mb():
    """Memori anonim nyata proses ini (tidak termasuk halaman memmap)."""
    try:
        with open("/proc/self/status") as f:
            for baris in f:
                if baris.startswith("RssAnon"):
                    return int(baris.split()[1]) // 1024
    except OSError:
        pass
    return 0


def status_ram():
    pakai = rss_anon_mb()
    if pakai >= MAKS_RAM_MB:
        return "kritis"
    if pakai >= PERINGATAN_RAM_MB:
        return "peringatan"
    return "aman"


def cek_parameter(jumlah):
    """Tolak calon otak yang melewati batas 110 juta."""
    if jumlah > MAKS_PARAMETER:
        raise ValueError(
            f"Ditolak: {jumlah:,} parameter melewati batas {MAKS_PARAMETER:,}"
        )
    return True
