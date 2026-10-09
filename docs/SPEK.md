# Spesifikasi OREKI v0.1

Cakupan: mesin penalaran kecil dalam Python murni (tanpa dependensi) yang
mewujudkan lapis 1 dan sebagian lapis 2 dari [KONSEP.md](KONSEP.md). Ini bukan
bahasa OREKI penuh; ini jembatan: pertanyaan terstruktur, basis hukum, dan
jawaban teraudit.

## 1. Pertanyaan terstruktur

```
hitung <simbol> ; nama = nilai satuan ; nama = nilai satuan ; ...
bisa nama = nilai satuan ; ...
```

Pemisah antar bagian: `;`. Desimal memakai koma. Satuan: `kg g m cm km s menit jam
N J kJ W Pa c`, digabung dengan `*` dan `/`, pangkat berupa angka di belakang
(`m/s2`). `c` adalah kecepatan cahaya (299.792.458 m/s). Nilai khusus teks:
`sistem = tertutup`.

## 2. Besaran dan dimensi

Dimensi dilacak sebagai pangkat (massa, panjang, waktu). Pecahan eksak dipakai
selama mungkin; akar menghasilkan float. Menjumlah atau membandingkan besaran
berbeda dimensi ditolak (`GalatDimensi`). Setiap data masukan dicek terhadap jenis
simbolnya (mis. `m` harus bermassa) sebelum dipakai.

## 3. Hukum

Tiap hukum berisi: rumus, penyelesai untuk tiap variabel, syarat berlaku, dan
fungsi batas yang menolak pemakaian di luar rentangnya. `python oreki.py cek`
memeriksa bahwa setiap penyelesai menghasilkan dimensi yang benar, dan tes
bolak-balik memastikan penyelesai antar variabel saling konsisten.

Basis awal (15): Hukum II Newton, momentum, impuls, percepatan rata-rata, GLB,
GLBB (tiga bentuk), energi kinetik, energi potensial, usaha, daya, gravitasi
Newton, tekanan, rapat massa.

Batas berlaku yang ditegakkan mesin:

- Hukum Newton ditolak bila ada kecepatan di data lebih dari 0,1 c (butuh relativitas).
- GLB hanya dipakai bila `a = 0` dinyatakan atau terbukti; bila `a` tidak nol, mesin
  memakai GLBB.

Hukum larangan (2): batas kecepatan cahaya untuk benda bermassa, dan kekekalan
energi pada sistem tertutup.

## 4. Rantai penalaran

Untuk `hitung X`, mesin mencari hukum yang bisa langsung menghitung X dari data;
bila tidak ada, ia menurunkan variabel yang kurang lewat hukum lain (maksimum 3
hukum perantara, rantai terpendek dulu, tanpa putaran). Bila dua hukum memberi hasil
berbeda untuk data yang sama, mesin memberi `PERINGATAN` bahwa data mungkin tidak
konsisten.

## 5. Status jawaban

| Status | Arti di v0.1 |
|---|---|
| (hasil) | Nilai hasil hitungan dengan rantai hukumnya |
| TIDAK | Sebuah hukum larangan dilanggar; hukumnya disebut |
| BELUM TAHU | Data kurang, hukum belum ada, atau di luar batas berlaku. Tidak menebak |
| DIIZINKAN HUKUM | Hukum yang diperiksa tidak melarang. Kelayakan rekayasa belum dinilai |
| DITOLAK | Pertanyaan atau data tidak sah (sintaks, satuan, dimensi) |

Catatan penyimpangan dari KONSEP.md: `BISA SEKARANG` dan `BISA NANTI` memerlukan
lapis 2 dan 3 (data material, energi, biaya) yang belum ada. Sampai itu ada, hukum
yang tidak melarang dilaporkan sebagai `DIIZINKAN HUKUM`, bukan `BISA`, agar tidak
mengklaim lebih dari yang dibuktikan.

## 6. Keputusan terbuka (usulan, belum final)

- Desimal: koma. Titik dicadangkan untuk pemisah pipeline bahasa.
- `A . 0 . B . 1`: belum diputuskan. Usulan: tulis satu contoh nyata
  (mis. rantai sebab-akibat) sebelum menetapkan arti angka 0/1.

## 7. Berikutnya

1. Menambah hukum hingga sekitar 20 dan 50 soal uji terstruktur.
2. Lapis sebab-akibat satu arah (`->`) sebagai graf yang ditulis manual.
3. Parser untuk sintaks bahasa (`F = m * a`, `a -> v -> s`).
4. Mode presisi (`cepat` / `teliti`) dan aritmetika interval.
