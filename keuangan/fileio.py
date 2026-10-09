"""Operasi baca, tambah, dan tulis file program."""

from pathlib import Path
from .validasi import validasi_baris


def buat_file_data(nama_file):
    """Membuat file data pertama kali memakai mode x."""
    try:
        with open(nama_file, "x", encoding="utf-8") as file:
            file.write("")
        return True
    except FileExistsError:
        # File lama tidak dihapus; program dapat terus memakai data yang ada.
        return False


def tambah_transaksi(nama_file, transaksi):
    """Menambahkan satu transaksi memakai mode a tanpa menghapus data lama."""
    with open(nama_file, "a", encoding="utf-8") as file:
        file.write(transaksi.ke_baris_file() + "\n")


def baca_transaksi(nama_file):
    """Membaca iteratif; baris rusak dilewati agar program tetap berjalan."""
    hasil = []
    try:
        with open(nama_file, "r", encoding="utf-8") as file:
            for baris in file:
                transaksi = validasi_baris(baris)
                if transaksi is not None:
                    hasil.append(transaksi)
    except FileNotFoundError:
        print(f"File data belum ada: {nama_file}")
    return hasil


def tulis_laporan(nama_file, ringkasan, transaksi_urut):
    """Menulis ulang laporan memakai mode w dan mengembalikan isi laporan."""
    baris = ["LAPORAN PENGELUARAN HARIAN", ""]
    baris.append(f"Jumlah transaksi: {ringkasan['jumlah']}")
    baris.append(f"Total pengeluaran: Rp{ringkasan['total']:,.0f}")
    baris.append(f"Rata-rata pengeluaran: Rp{ringkasan['rata_rata']:,.0f}")
    baris.append(f"Transaksi besar: {ringkasan['transaksi_besar']}")
    baris.append("")
    baris.append("DAFTAR TRANSAKSI DARI NOMINAL TERBESAR")
    baris.extend(item.tampilkan() for item in transaksi_urut)
    isi = "\n".join(baris)
    with open(nama_file, "w", encoding="utf-8") as file:
        file.write(isi)
    return isi
