"""Validasi input pengguna dan record transaksi."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any


class DataTransaksiError(ValueError):
    """Kesalahan data yang dapat dijelaskan kepada pengguna."""


def teks_wajib(nilai: Any, nama_field: str) -> str:
    """Mengembalikan teks bersih atau menolak field wajib yang kosong."""
    teks = str(nilai).strip()
    if not teks:
        raise DataTransaksiError(f"{nama_field} tidak boleh kosong.")
    return teks


def tanggal_valid(nilai: Any) -> str:
    """Memvalidasi tanggal format YYYY-MM-DD dan mengembalikannya secara konsisten."""
    tanggal = teks_wajib(nilai, "Tanggal")
    try:
        return datetime.strptime(tanggal, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError as error:
        raise DataTransaksiError(
            "Tanggal harus memakai format YYYY-MM-DD dan merupakan tanggal yang valid."
        ) from error


def nominal_valid(nilai: Any) -> Decimal:
    """Mengubah nominal ke Decimal; nol dan nilai negatif sengaja ditolak."""
    teks = teks_wajib(nilai, "Nominal").replace("Rp", "").replace(" ", "")

    # Terima format umum Indonesia (10.000,50) dan format titik desimal (10000.50).
    if "," in teks and "." in teks:
        if teks.rfind(",") > teks.rfind("."):
            teks = teks.replace(".", "").replace(",", ".")
        else:
            teks = teks.replace(",", "")
    elif "," in teks:
        teks = teks.replace(",", ".")
    elif teks.count(".") > 1:
        teks = teks.replace(".", "")
    elif "." in teks:
        bagian_kiri, bagian_kanan = teks.split(".", maxsplit=1)
        # Pada konteks Rupiah, 10.000 paling lazim berarti sepuluh ribu.
        if bagian_kiri.isdigit() and bagian_kanan.isdigit() and len(bagian_kanan) == 3:
            teks = bagian_kiri + bagian_kanan

    try:
        nominal = Decimal(teks)
    except (InvalidOperation, ValueError) as error:
        raise DataTransaksiError("Nominal harus berupa angka, misalnya 25000.") from error

    if nominal <= 0:
        # raise dipakai untuk validasi input pengguna, bukan assert.
        raise DataTransaksiError("Nominal harus lebih dari nol.")
    return nominal.quantize(Decimal("0.01"))


def catatan_valid(nilai: Any) -> str:
    """Membersihkan catatan opsional agar format file tetap aman dibaca."""
    return str(nilai or "").strip().replace("\n", " ")


def record_valid(record: dict[str, Any]) -> dict[str, Any]:
    """Memvalidasi record dari file sebelum dibuat menjadi objek Transaksi."""
    field_wajib = {"id", "tanggal", "kategori", "nominal", "catatan"}
    if not isinstance(record, dict) or not field_wajib.issubset(record):
        raise DataTransaksiError("Struktur record transaksi tidak lengkap.")

    identitas = teks_wajib(record["id"], "ID transaksi")
    if not identitas.isalnum() or len(identitas) < 6:
        raise DataTransaksiError("ID transaksi tidak valid.")

    return {
        "id": identitas,
        "tanggal": tanggal_valid(record["tanggal"]),
        "kategori": teks_wajib(record["kategori"], "Kategori"),
        "nominal": nominal_valid(record["nominal"]),
        "catatan": catatan_valid(record["catatan"]),
    }
