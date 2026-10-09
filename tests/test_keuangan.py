"""Pengujian global memakai library unittest."""

import unittest
from pathlib import Path

from keuangan.fileio import baca_transaksi, tambah_transaksi, buat_file_data
from keuangan.models import BukuKeuangan, Transaksi
from keuangan.processing import buat_ringkasan, buat_transaksi, hitung_total, urutkan_transaksi
from keuangan.validasi import validasi_transaksi


class TestKeuangan(unittest.TestCase):
    """Minimal lima pengujian untuk fungsi inti program."""

    def test_hitung_total(self):
        self.assertEqual(hitung_total(5000, 7000, 8000), 20000)

    def test_validasi_nominal_negatif(self):
        with self.assertRaises(ValueError):
            validasi_transaksi("2026-10-01", "Makan", -1000)

    def test_buat_transaksi_kwargs(self):
        data = buat_transaksi(tanggal="2026-10-01", kategori="Makan", nominal=12000)
        self.assertEqual(data.kategori, "Makan")

    def test_urutkan_transaksi(self):
        data = [Transaksi("1", "A", 1000), Transaksi("2", "B", 5000)]
        self.assertEqual(urutkan_transaksi(data)[0].nominal, 5000)

    def test_ringkasan(self):
        data = [Transaksi("1", "A", 1000), Transaksi("2", "B", 3000)]
        self.assertEqual(buat_ringkasan(data, batas_besar=2000)["transaksi_besar"], 1)

    def test_file_baca_dan_tambah(self):
        nama_file = Path(__file__).parent / "data_uji.txt"
        if nama_file.exists():
            nama_file.unlink()
        self.assertTrue(buat_file_data(nama_file))
        tambah_transaksi(nama_file, Transaksi("2026-10-01", "Makan", 10000, "Uji"))
        self.assertEqual(len(baca_transaksi(nama_file)), 1)
        nama_file.unlink()

    def test_buku_keuangan_total(self):
        buku = BukuKeuangan()
        buku.tambah(Transaksi("1", "A", 2000))
        self.assertEqual(buku.total(), 2000)


if __name__ == "__main__":
    unittest.main()
