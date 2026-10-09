# OREKI (Embrio)

Mesin penalaran yang menjawab dari **hukum alam**, bukan dari kebiasaan teks.
Setiap jawaban punya rantai alasan yang bisa diaudit, dan setiap "TIDAK" wajib
menyebut hukum yang melarangnya.

Status: **v0.1**, draf kerja. Konsep lengkap ada di [docs/KONSEP.md](docs/KONSEP.md),
spesifikasi v0.1 di [docs/SPEK.md](docs/SPEK.md).

## Yang sudah jalan

- Besaran bersatuan: setiap nilai membawa dimensinya, rumus yang dimensinya
  tidak cocok langsung ditolak.
- Basis 15 hukum persamaan (kinematika dan dinamika Newton) dan 2 hukum
  larangan (batas cahaya, kekekalan energi), masing-masing dengan batas berlaku.
- Rantai hukum: jawaban bisa diturunkan lewat beberapa hukum, lengkap dengan
  langkahnya.
- Jawaban jujur: `TIDAK`, `BELUM TAHU`, `DIIZINKAN HUKUM`, atau hasil hitungan.
  Tidak menebak di luar batas berlaku hukum.

## Pakai (Python 3.10+, tanpa dependensi)

```
python oreki.py tanya "hitung F ; m = 2 kg ; a = 3 m/s2"
python oreki.py tanya "bisa v = 1,5 c ; m = 1 kg"
python oreki.py demo     # contoh jawaban
python oreki.py hukum    # daftar hukum dan syaratnya
python oreki.py cek      # periksa konsistensi dimensi semua hukum
python oreki.py uji      # jalankan tes otomatis
python oreki.py chat     # tanya jawab interaktif
```

Desimal ditulis dengan koma (`9,8 m/s2`); titik dicadangkan untuk bahasa OREKI.

## Struktur

```
oreki.py        perintah utama
inti/           satuan, hukum, larangan, pembaca, mesin
tes/            tes otomatis
docs/           konsep dan spesifikasi
```
