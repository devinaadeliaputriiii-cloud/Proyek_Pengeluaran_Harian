"""Fungsi validasi input dan data file."""


def validasi_transaksi(tanggal, kategori, nominal):
    """Memeriksa field wajib dan nominal agar data tidak salah."""
    if not tanggal.strip() or not kategori.strip():
        raise ValueError("Tanggal dan kategori tidak boleh kosong.")
    try:
        nominal_angka = float(nominal)
    except ValueError as error:
        raise ValueError("Nominal harus berupa angka.") from error
    if nominal_angka <= 0:
        raise ValueError("Nominal harus lebih dari nol.")
    return nominal_angka


def validasi_baris(baris):
    """Mengubah satu baris file menjadi Transaksi atau mengembalikan None."""
    from .models import Transaksi
    bagian = baris.strip().split(";")
    if len(bagian) != 4:
        return None
    try:
        nominal = validasi_transaksi(bagian[0], bagian[1], bagian[2])
    except ValueError:
        return None
    return Transaksi(bagian[0], bagian[1], nominal, bagian[3])
