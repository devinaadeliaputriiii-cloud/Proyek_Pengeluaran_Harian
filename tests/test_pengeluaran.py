"""Pengujian otomatis aplikasi pengeluaran memakai unittest dan file sementara."""

from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from keuangan.fileio import RepositoryTransaksi
from keuangan.laporan import susun_laporan, tulis_laporan
from keuangan.models import Transaksi
from keuangan.processing import AnalisisPengeluaran, buat_transaksi, hitung_total
from keuangan.validasi import DataTransaksiError, tanggal_valid


TEST_TEMP_ROOT = Path(__file__).resolve().parent / ".test_runtime"


class TestPengeluaranHarian(unittest.TestCase):
    """Menggunakan folder sementara sehingga data pengguna tidak pernah diubah."""

    def setUp(self) -> None:
        # Lokasi sementara berada di proyek agar kompatibel dengan sandbox Windows,
        # dan tetap terpisah dari folder data pengguna.
        TEST_TEMP_ROOT.mkdir(exist_ok=True)
        self.folder = tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT)
        self.file_data = Path(self.folder.name) / "transaksi.jsonl"
        self.repo = RepositoryTransaksi(self.file_data)
        self.data = [
            Transaksi("2026-10-01", "Makan", Decimal("25000"), "Makan siang"),
            Transaksi("2026-10-02", "Transportasi", Decimal("15000"), "Bus kampus"),
            Transaksi("2026-10-03", "Belanja", Decimal("120000"), "Buku"),
        ]

    def tearDown(self) -> None:
        self.folder.cleanup()

    def test_hitung_total_menggunakan_args(self) -> None:
        self.assertEqual(
            hitung_total(Decimal("5000"), Decimal("7000"), Decimal("8000")),
            Decimal("20000"),
        )

    def test_buat_transaksi_menggunakan_kwargs(self) -> None:
        transaksi = buat_transaksi(
            tanggal="2026-10-01",
            kategori="Makan",
            nominal="12000",
            catatan="Uji",
        )
        self.assertEqual(transaksi.kategori, "Makan")
        self.assertEqual(transaksi.nominal, Decimal("12000.00"))

    def test_tanggal_tidak_valid_ditolak(self) -> None:
        with self.assertRaises(DataTransaksiError):
            tanggal_valid("2026-02-30")

    def test_nominal_nol_ditolak(self) -> None:
        with self.assertRaises(DataTransaksiError):
            buat_transaksi(tanggal="2026-10-01", kategori="Makan", nominal=0)

    def test_urutkan_nominal_terbesar(self) -> None:
        urut = AnalisisPengeluaran(self.data).urutkan_nominal()
        self.assertEqual(urut[0].kategori, "Belanja")
        self.assertEqual(urut[-1].kategori, "Transportasi")

    def test_cari_transaksi(self) -> None:
        hasil = AnalisisPengeluaran(self.data).cari("kampus")
        self.assertEqual(len(hasil), 1)
        self.assertEqual(hasil[0].kategori, "Transportasi")

    def test_ringkasan_total_rata_rata_dan_transaksi_besar(self) -> None:
        ringkasan = AnalisisPengeluaran(self.data).buat_ringkasan(
            batas_transaksi_besar=Decimal("100000")
        )
        self.assertEqual(ringkasan["total"], Decimal("160000.00"))
        self.assertEqual(ringkasan["rata_rata"], Decimal("53333.33"))
        self.assertEqual(ringkasan["jumlah_transaksi_besar"], 1)

    def test_file_x_a_r_dan_persistensi(self) -> None:
        self.assertTrue(self.repo.buat_file_pertama_kali())
        self.assertFalse(self.repo.buat_file_pertama_kali())
        self.repo.tambah(self.data[0])
        self.repo.tambah(self.data[1])
        dibaca = self.repo.baca().transaksi
        self.assertEqual([item.kategori for item in dibaca], ["Makan", "Transportasi"])

    def test_baris_rusak_dilewati(self) -> None:
        self.repo.buat_file_pertama_kali()
        self.repo.tambah(self.data[0])
        with open(self.file_data, "a", encoding="utf-8") as file:
            file.write("{ini bukan json}\n")
        hasil = self.repo.baca()
        self.assertEqual(len(hasil.transaksi), 1)
        self.assertEqual(hasil.baris_rusak, 1)

    def test_hapus_transaksi_memperbarui_file(self) -> None:
        self.repo.tambah(self.data[0])
        self.repo.tambah(self.data[1])
        terhapus = self.repo.hapus_berdasarkan_id(self.data[0].id)
        self.assertEqual(terhapus.id, self.data[0].id)
        self.assertEqual(len(self.repo.baca().transaksi), 1)

    def test_laporan_dibuat_dengan_mode_w(self) -> None:
        analisis = AnalisisPengeluaran(self.data)
        isi = susun_laporan(
            analisis.buat_ringkasan(batas_transaksi_besar=Decimal("100000")),
            analisis.urutkan_nominal(),
        )
        file_laporan = Path(self.folder.name) / "laporan.txt"
        tulis_laporan(file_laporan, isi)
        self.assertTrue(file_laporan.exists())
        self.assertIn("LAPORAN PENGELUARAN HARIAN", file_laporan.read_text(encoding="utf-8"))

    def test_json_record_valid_dapat_dibaca(self) -> None:
        """Memastikan format yang disimpan adalah JSON Lines yang dapat dimuat ulang."""
        self.repo.tambah(self.data[0])
        record = json.loads(self.file_data.read_text(encoding="utf-8"))
        self.assertEqual(record["id"], self.data[0].id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
