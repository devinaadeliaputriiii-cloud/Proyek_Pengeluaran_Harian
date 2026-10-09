"""Menjalankan program pencatatan pengeluaran harian."""

from pathlib import Path

from keuangan.fileio import buat_file_data, tambah_transaksi, baca_transaksi, tulis_laporan
from keuangan.models import Transaksi
from keuangan.processing import buat_ringkasan, urutkan_transaksi


DATA_FILE = Path("data/transaksi.txt")
LAPORAN_FILE = Path("laporan/laporan_keuangan.txt")


def siapkan_folder():
    """Membuat folder data dan laporan bila belum tersedia."""
    DATA_FILE.parent.mkdir(exist_ok=True)
    LAPORAN_FILE.parent.mkdir(exist_ok=True)


def isi_data_contoh():
    """Menambahkan data contoh hanya jika file data masih kosong."""
    transaksi_lama = baca_transaksi(DATA_FILE)
    if transaksi_lama:
        return

    contoh = [
        Transaksi("2026-10-01", "Makan", 25000, "Makan siang"),
        Transaksi("2026-10-02", "Transportasi", 15000, "Ojek kampus"),
        Transaksi("2026-10-03", "Makan", 18000, "Sarapan"),
    ]
    for transaksi in contoh:
        tambah_transaksi(DATA_FILE, transaksi)


def jalankan_program(tampilkan_detail=True):
    """Menyiapkan data, membuat laporan, lalu mengembalikan isi laporan."""
    siapkan_folder()
    buat_file_data(DATA_FILE)
    isi_data_contoh()

    transaksi = baca_transaksi(DATA_FILE)
    # keyword argument dipakai agar maksud parameter mudah dibaca.
    ringkasan = buat_ringkasan(transaksi, batas_besar=20000)
    transaksi_urut = urutkan_transaksi(transaksi, menurun=True)
    isi_laporan = tulis_laporan(LAPORAN_FILE, ringkasan, transaksi_urut)

    if tampilkan_detail:
        print(isi_laporan)
    return isi_laporan


if __name__ == "__main__":
    # Blok ini hanya berjalan saat main.py dijalankan langsung.
    jalankan_program(tampilkan_detail=True)
