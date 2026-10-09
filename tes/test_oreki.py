import os
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inti.galat import GalatDimensi, GalatMatematika, GalatSatuan
from inti.hukum import BASIS, JENIS, KONSTANTA, SIMBOL, cek_konsistensi
from inti.mesin import jawab
from inti.satuan import Besaran, parse_besaran


def hasil(teks):
    j = jawab(teks)
    return j.status, (str(j.hasil) if j.hasil is not None else None), j


class TesSatuan(unittest.TestCase):
    def test_parse_dan_kali(self):
        self.assertEqual(str(parse_besaran("2 kg") * parse_besaran("3 m/s2")), "6 N")

    def test_desimal_koma_eksak(self):
        self.assertEqual(parse_besaran("0,5 kg").nilai, Fraction(1, 2))

    def test_konversi_satuan(self):
        self.assertEqual(str(parse_besaran("2 jam")), "7200 s")
        self.assertEqual(parse_besaran("1 km"), parse_besaran("1000 m"))

    def test_jumlah_beda_dimensi_ditolak(self):
        with self.assertRaises(GalatDimensi):
            parse_besaran("2 kg") + parse_besaran("3 m/s2")

    def test_satuan_tak_dikenal(self):
        with self.assertRaises(GalatSatuan):
            parse_besaran("2 xyz")

    def test_akar_negatif_ditolak(self):
        with self.assertRaises(GalatMatematika):
            parse_besaran("-4 m2") ** Fraction(1, 2)

    def test_bagi_nol_ditolak(self):
        with self.assertRaises(GalatMatematika):
            parse_besaran("1 kg") / parse_besaran("0 m")


class TesBasisHukum(unittest.TestCase):
    def test_semua_hukum_konsisten_dimensinya(self):
        self.assertEqual(cek_konsistensi(), [])

    def test_simbol_terdaftar(self):
        for h in BASIS:
            for s in h.variabel:
                self.assertIn(SIMBOL[s], JENIS)

    def test_bolak_balik_tiap_hukum(self):
        """Hitung satu variabel dari yang lain, lalu cari tiap variabel lain
        dari hasilnya: semua harus kembali ke nilai awal."""
        for h in BASIS:
            nilai = {s: Besaran(Fraction(2 + i, 1), JENIS[SIMBOL[s]])
                     for i, s in enumerate(h.variabel)}
            dasar = next(iter(h.selesaikan))
            v = {s: nilai[s] for s in h.variabel if s != dasar}
            v.update({k: KONSTANTA[k] for k in h.konstanta})
            nilai[dasar] = h.selesaikan[dasar](v)
            for target, fungsi in h.selesaikan.items():
                bahan = {s: nilai[s] for s in h.variabel if s != target}
                bahan.update({k: KONSTANTA[k] for k in h.konstanta})
                dapat = float(fungsi(bahan).nilai)
                asli = float(nilai[target].nilai)
                self.assertAlmostEqual(dapat / asli, 1.0, places=9,
                                       msg=f"{h.id}.{target}")


class TesHitung(unittest.TestCase):
    def test_newton2(self):
        self.assertEqual(hasil("hitung F ; m = 2 kg ; a = 3 m/s2")[:2], ("HASIL", "6 N"))

    def test_massa_dari_gaya(self):
        self.assertEqual(hasil("hitung m ; F = 6 N ; a = 3 m/s2")[:2], ("HASIL", "2 kg"))

    def test_rantai_tiga_hukum(self):
        st, h, j = hasil("hitung Ek ; F = 10 N ; m = 2 kg ; t = 3 s ; v0 = 0 m/s")
        self.assertEqual((st, h), ("HASIL", "225 J"))
        self.assertEqual(len(j.langkah), 3)

    def test_konversi_masukan(self):
        self.assertEqual(hasil("hitung s ; v = 36 km/jam ; t = 2 menit ; a = 0 m/s2")[:2],
                         ("HASIL", "1200 m"))

    def test_energi_potensial_g_bawaan(self):
        st, h, _ = hasil("hitung Ep ; m = 2 kg ; h = 10 m")
        self.assertEqual(st, "HASIL")
        self.assertEqual(h, "196,133 J")

    def test_gravitasi_butuh_akar(self):
        st, h, _ = hasil("hitung r ; F = 1 N ; m1 = 1e10 kg ; m2 = 1e10 kg")
        self.assertEqual(st, "HASIL")
        self.assertTrue(h.endswith(" m"))

    def test_glb_butuh_a_nol(self):
        self.assertEqual(hasil("hitung v ; s = 100 m ; t = 20 s")[0], "BELUM TAHU")
        self.assertEqual(hasil("hitung v ; s = 100 m ; t = 20 s ; a = 0 m/s2")[:2],
                         ("HASIL", "5 m/s"))

    def test_glb_ditolak_bila_a_tidak_nol(self):
        # GLB (s = v*t) tidak boleh dipakai saat a = 2; mesin harus memakai GLBB
        # dan hasilnya 25 m/s (v0 = -15 m/s, v = v0 + a*t), bukan 5 m/s.
        st, h, j = hasil("hitung v ; s = 100 m ; t = 20 s ; a = 2 m/s2")
        self.assertEqual((st, h), ("HASIL", "25 m/s"))
        self.assertNotIn("Gerak lurus beraturan", [l.hukum.nama for l in j.langkah])

    def test_di_luar_batas_newton(self):
        st, _, j = hasil("hitung F ; m = 1 kg ; a = 3 m/s2 ; v = 1e8 m/s")
        self.assertEqual(st, "BELUM TAHU")
        self.assertTrue(any("relativitas" in a for a in j.alasan))

    def test_data_tidak_konsisten_diperingatkan(self):
        st, _, j = hasil("hitung a ; F = 10 N ; m = 2 kg ; dv = 6 m/s ; t = 2 s")
        self.assertEqual(st, "HASIL")
        self.assertTrue(j.peringatan)

    def test_dimensi_input_salah_ditolak(self):
        self.assertEqual(hasil("hitung F ; m = 2 s ; a = 3 m/s2")[0], "DITOLAK")

    def test_simbol_tak_dikenal_ditolak(self):
        self.assertEqual(hasil("hitung Z ; m = 2 kg")[0], "DITOLAK")

    def test_data_kurang_belum_tahu(self):
        self.assertEqual(hasil("hitung F ; m = 2 kg")[0], "BELUM TAHU")

    def test_bagi_nol_tidak_meledak(self):
        self.assertIn(hasil("hitung m ; F = 6 N ; a = 0 m/s2")[0], ("BELUM TAHU", "DITOLAK"))

    def test_sintaks_salah(self):
        self.assertEqual(hasil("")[0], "DITOLAK")
        self.assertEqual(hasil("hitung")[0], "DITOLAK")
        self.assertEqual(hasil("ramal F ; m = 1 kg")[0], "DITOLAK")


class TesBisa(unittest.TestCase):
    def test_lebih_cepat_dari_cahaya(self):
        st, _, j = hasil("bisa v = 1,5 c ; m = 1 kg")
        self.assertEqual(st, "TIDAK")
        self.assertTrue(j.hukum and j.alasan)

    def test_cahaya_tanpa_massa_belum_tahu(self):
        self.assertEqual(hasil("bisa v = 1,5 c")[0], "BELUM TAHU")

    def test_di_bawah_cahaya_diizinkan_hukum(self):
        self.assertEqual(hasil("bisa v = 0,5 c ; m = 1 kg")[0], "DIIZINKAN HUKUM")

    def test_energi_dari_nol(self):
        st, _, _ = hasil("bisa E_masuk = 100 J ; E_keluar = 120 J ; sistem = tertutup")
        self.assertEqual(st, "TIDAK")

    def test_sistem_terbuka_belum_tahu(self):
        st, _, _ = hasil("bisa E_masuk = 100 J ; E_keluar = 120 J ; sistem = terbuka")
        self.assertEqual(st, "BELUM TAHU")

    def test_tanpa_hukum_relevan(self):
        self.assertEqual(hasil("bisa m = 1 kg")[0], "BELUM TAHU")


if __name__ == "__main__":
    unittest.main()
