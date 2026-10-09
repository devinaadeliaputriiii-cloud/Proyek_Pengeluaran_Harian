"""Pembuatan laporan teks untuk pengeluaran harian."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import Transaksi


def format_rupiah(nominal: object) -> str:
    """Memformat angka sebagai Rupiah dengan dua angka desimal."""
    return f"Rp{nominal:,.2f}"


def susun_laporan(ringkasan: dict[str, object], transaksi_urut: Iterable[Transaksi]) -> str:
    """Menyusun isi laporan tanpa menyentuh file agar mudah diuji."""
    baris = [
        "LAPORAN PENGELUARAN HARIAN",
        "=" * 33,
        f"Jumlah transaksi           : {ringkasan['jumlah']}",
        f"Total pengeluaran          : {format_rupiah(ringkasan['total'])}",
        f"Rata-rata pengeluaran      : {format_rupiah(ringkasan['rata_rata'])}",
        f"Batas transaksi besar      : {format_rupiah(ringkasan['batas_transaksi_besar'])}",
        f"Jumlah transaksi besar     : {ringkasan['jumlah_transaksi_besar']}",
        "",
        "TOTAL PER KATEGORI",
    ]

    kategori = ringkasan["per_kategori"]
    if kategori:
        baris.extend(f"- {nama}: {format_rupiah(total)}" for nama, total in kategori.items())
    else:
        baris.append("- Belum ada transaksi.")

    baris.extend(["", "TRANSAKSI DARI NOMINAL TERBESAR"])
    daftar = list(transaksi_urut)
    if daftar:
        baris.extend(item.tampilkan() for item in daftar)
    else:
        baris.append("- Belum ada transaksi.")
    return "\n".join(baris) + "\n"


def tulis_laporan(file_laporan: Path | str, isi_laporan: str) -> Path:
    """Menulis laporan menggunakan mode w setelah folder laporan disiapkan."""
    tujuan = Path(file_laporan)
    tujuan.parent.mkdir(parents=True, exist_ok=True)
    with open(tujuan, "w", encoding="utf-8") as file:
        file.write(isi_laporan)
    return tujuan
