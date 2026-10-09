# OREKI: Kumpulan Konsep Proyek

Dokumen hidup. Versi 0.1 (draf konsep, belum spesifikasi final).

## 1. Visi

OREKI adalah rancangan bahasa dan mesin penalaran dengan sintaks, aljabar, dan
aturan sendiri. Tujuan jangka panjangnya menyatukan fisika, matematika, presisi,
dan sebab-akibat dalam satu bahasa yang ringkas, sehingga pengguna tidak perlu
menyentuh kerumitan bahasa tingkat rendah. OREKI (juga disebut "embrio") menalar
dari hukum alam, bukan dari kebiasaan teks seperti LLM.

Rumusan: OREKI menjawab apa yang diizinkan alam, apa yang dilarang beserta
alasannya, dan apa yang harus ditemukan agar yang diizinkan itu menjadi nyata.

## 2. Prinsip inti

1. **Satu bahasa, semua lapisan.** Fisika, matematika, presisi, dan sebab-akibat
   hidup dalam satu bahasa.
2. **Bahasa buatan sendiri.** Sintaks dan aljabar dirancang sendiri.
3. **Pengguna menulis niat, mesin mengurus detail.**
4. **Hukum alam sebagai fondasi permanen.** Pengetahuan baru boleh tumbuh, tetapi
   harus lolos pemeriksaan terhadap hukum dasar.
5. **Setiap jawaban bisa diaudit.** Tidak ada jawaban tanpa rantai alasan.

## 3. Huruf, aljabar, presisi

Huruf membawa makna dan dimensi. Pencocokan dijaga dua lapis: cocok secara
simbol dan cocok secara satuan. Rumus yang dimensinya tidak konsisten langsung
ditolak.

| Teknik | Manfaat | Harga |
|---|---|---|
| Pecahan eksak (rasional) | Tanpa galat pembulatan | Lebih lambat |
| Aritmetika interval | Galat dilacak otomatis | Sekitar 2-3x lebih lambat |
| Pelacakan satuan | Menangkap kesalahan rumus | Overhead kompilasi kecil |
| Cepat (int8/float32) | Kecepatan dan hemat memori | Presisi lebih rendah |

Mode presisi (gagasan): pengguna memilih `cepat` atau `teliti`.

## 4. Sintaks (rancangan awal)

Gaya titik sebagai pemisah, mirip pipeline.

```
A . 0 . B . 1     # contoh dasar dari pencipta (arti belum diputuskan)
F . m . a         # fisika: huruf = besaran
F = m * a         # matematika: persamaan (dua arah)
F -> a            # sebab: gaya menyebabkan percepatan
m -| a            # berbanding terbalik
a -> v -> s       # rantai sebab
```

Simbol (usulan): `.` pemisah/penerus hasil, `=` persamaan dua arah, `->` sebab
menuju akibat (satu arah), `-|` berbanding terbalik.

## 5. Tiga jenis hubungan

| Jenis | Contoh | Sifat |
|---|---|---|
| Persamaan | `F = m * a` | Dua arah, bisa dibalik |
| Sebab-akibat | gaya -> percepatan | Satu arah |
| Korelasi | es krim naik, tenggelam naik | Muncul bersama, bukan sebab |

Hubungan kausal inti ditulis manual terlebih dahulu, karena sebab-akibat tidak
bisa dipelajari hanya dari teks atau data.

## 6. Fondasi tiga lapis

```
Lapis 1 (tetap)  : aturan matematika + aturan dimensi/satuan
Lapis 2 (tetap)  : hukum fisika dasar + rantai sebab-akibatnya
Lapis 3 (tumbuh) : pengetahuan baru, diperiksa terhadap lapis 1 dan 2
```

Konsep baru yang bertentangan dengan kekekalan energi atau aturan dimensi ditolak.

## 7. Cara OREKI menjawab

Ketika ditanya "apakah ini bisa?", OREKI mencocokkan dengan hukum alam. Jika hukum
tidak mengizinkan, jawabannya tidak, walaupun terdengar masuk akal, lalu OREKI
menjelaskan mengapa.

| Status | Arti |
|---|---|
| BISA SEKARANG | Rantai hukum membuktikannya dan teknologi tersedia |
| BISA NANTI | Hukum mengizinkan, syarat rekayasa belum terpenuhi; OREKI menyebut apa yang harus ditemukan dulu |
| TIDAK | Hukum melarangnya, disertai alasan |
| BELUM TAHU | Tidak ada hukum yang menjawab. Jujur, tidak menebak |

"Tidak ada aturan yang membolehkan" tidak sama dengan "aturan melarang".

Format jawaban:

```
JAWABAN     : TIDAK
HUKUM       : kekekalan energi (berlaku: sistem tertutup)
ALASAN      : energi keluar > energi masuk, tidak mungkin
KEPERCAYAAN : tinggi (hukum teruji luas)
```

## 8. Tiga lapis makna "bisa"

| Lapis | Pertanyaan |
|---|---|
| Diizinkan hukum | Apakah hukum alam melarangnya? |
| Layak secara rekayasa | Apakah material, energi, dan biaya memungkinkan? |
| Siap hari ini | Apakah sudah bisa dibuat sekarang? |

Kekuatan OREKI ada di lapis pertama: menunjukkan bahwa yang menghalangi bukan
alam, melainkan material atau energi yang belum ada.

## 9. Pencarian sebab-akibat yang belum pernah dilihat

Mesin menurunkan konsekuensi dari hukum alam sehingga dapat menemukan
sebab-akibat yang belum pernah dilihat manusia. Preseden: Neptunus ditemukan lewat
hitungan sebelum dilihat teleskop, positron diprediksi sebelum terdeteksi,
gelombang gravitasi diprediksi sekitar seratus tahun sebelum terukur.

```
hukum -> turunkan prediksi baru -> uji (eksperimen/data)
cocok?        perkuat hukum
tidak cocok?  hukum perlu diperbaiki
```

Mutasi diri yang sehat terjadi ketika prediksi berbenturan dengan data nyata,
bukan dengan kesimpulan mesin sendiri.

## 10. Arsitektur dan memori

- **Lapisan pengguna:** bahasa OREKI, ringkas, tanpa tipe rumit, pointer, atau header.
- **Lapisan mesin:** compiler, mesin tensor dan autograd, penyimpanan memori.
- **Memori fluida:** data dikompresi menjadi koordinat hubungan konsep (embedding
  terkuantisasi dan memory-mapped files agar hemat RAM di HP).

```
skrip .oreki -> parser/VM kecil -> tensor + autograd
             -> memori konsep terkuantisasi
             -> gating terlatih + loop hadiah
```

## 11. Alur kerja sistem

1. **Ingestion:** mengambil data mentah secara berkala.
2. **Compression:** mengubah data menjadi koordinat konsep abstrak.
3. **Evaluation:** menguji konsistensi konsep baru terhadap hukum yang mapan.
4. **Mutation:** memperbarui bobot dan struktur berdasarkan evaluasi dan sinyal
   hadiah/penalti.

## 12. Tiga inovasi utama (versi pencipta)

1. In-Engine Logic Shift: keputusan dikendalikan oleh gerbang matematika internal.
2. Dynamic Zero-RAG Memory: kompresi data menjadi koordinat konsep.
3. Native Self-Mutation: evolusi berbasis hadiah tertanam di tingkat bahasa.

## 13. Batas jujur yang dijaga

- Gerbang matematika tetap dijalankan kode level bawah. Yang realistis adalah
  percabangan lunak berbasis bobot.
- Belajar butuh ukuran benar/salah (hadiah), aturan pembaruan, dan pengulangan.
- Mesin deduktif hanya sepintar hukum yang dimasukkan. Setiap hukum menyertakan
  batas berlakunya.
- "TIDAK" hanya sekuat hukum yang dipakai. Setiap "TIDAK" wajib menyebut hukumnya.
- Menerjemahkan kalimat bebas menjadi simbol adalah bagian tersulit. Tahap awal
  memakai pertanyaan terstruktur.
- OREKI tidak memprediksi kapan atau apakah suatu penemuan terjadi, hanya syarat
  yang harus dipenuhi.
- Klaim "lebih akurat dari LLM" perlu tolok ukur. Rumusan jujur: lebih eksak dan
  terverifikasi untuk soal yang terformalkan.
- Istilah "6GL" tidak punya standar resmi, tidak dipakai sebagai klaim teknis.

## 14. Peta jalan

1. Spesifikasi v0.1: simbol, besaran bersatuan, hukum beserta batas berlakunya, status jawaban. **(ada: docs/SPEK.md)**
2. Parser dan VM kecil.
3. Mesin tensor dan autograd.
4. Notasi aljabar dan mode presisi.
5. Basis hukum awal: kinematika dan dinamika Newton (sekitar 20 rumus). **(15 rumus ada)**
6. Pemeriksa dimensi dan penyelesai aljabar. **(pemeriksa dimensi ada)**
7. Uji: sekitar 50 soal, bandingkan dengan LLM.
8. Memori konsep dan loop hadiah (self-mutation yang terverifikasi).

## 15. Pertanyaan terbuka

- Apa arti tepat `A . 0 . B . 1` dan angka 0/1?
- Bagaimana desimal ditulis agar tidak bentrok dengan titik? (v0.1: koma)
- Seberapa ketat format penulisan hukum beserta batas berlakunya?
- Dari mana sumber kebenaran untuk menguji prediksi baru?
- Domain mana setelah fisika dan matematika dasar?
