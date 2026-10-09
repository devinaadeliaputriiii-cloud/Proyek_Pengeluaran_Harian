"""Fungsi dan class untuk pencarian serta analisis pengeluaran."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from .models import Transaksi


def hitung_total(*nominal: Decimal) -> Decimal:
    """Menjumlahkan jumlah nominal yang fleksibel menggunakan *args."""
    return sum(nominal, Decimal("0"))


def buat_transaksi(**data: object) -> Transaksi:
    """Membuat transaksi dari atribut dinamis melalui **kwargs."""
    return Transaksi(**data)


class AnalisisPengeluaran:
    """Mengolah daftar transaksi tanpa mengubah urutan data asli."""

    def __init__(self, transaksi: Iterable[Transaksi]) -> None:
        self.transaksi = list(transaksi)

    def urutkan_nominal(self, menurun: bool = True) -> list[Transaksi]:
        """Mengurutkan transaksi memakai lambda sebagai key."""
        return sorted(self.transaksi, key=lambda item: item.nominal, reverse=menurun)

    def cari(self, kata_kunci: str) -> list[Transaksi]:
        """Mencari kata pada tanggal, kategori, atau catatan tanpa peka huruf besar."""
        kata = kata_kunci.strip().casefold()
        if not kata:
            return []
        cocok = lambda item: kata in (
            f"{item.tanggal} {item.kategori} {item.catatan}".casefold()
        )
        return list(filter(cocok, self.transaksi))

    def total(self) -> Decimal:
        """Menghitung total dengan meneruskan nilai melalui *args."""
        return hitung_total(*(item.nominal for item in self.transaksi))

    def rata_rata(self) -> Decimal:
        """Menghitung rata-rata atau nol jika belum ada transaksi."""
        if not self.transaksi:
            return Decimal("0")
        return (self.total() / len(self.transaksi)).quantize(Decimal("0.01"))

    def per_kategori(self) -> dict[str, Decimal]:
        """Mengelompokkan total nominal berdasarkan kategori."""
        hasil: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for item in self.transaksi:
            hasil[item.kategori] += item.nominal
        return dict(sorted(hasil.items(), key=lambda pasangan: pasangan[1], reverse=True))

    def buat_ringkasan(self, batas_transaksi_besar: Decimal = Decimal("100000")) -> dict[str, object]:
        """Membuat data ringkasan yang digunakan menu dan laporan."""
        if batas_transaksi_besar <= 0:
            raise ValueError("Batas transaksi besar harus lebih dari nol.")

        total = self.total()
        transaksi_besar = [
            item for item in self.transaksi if item.nominal >= batas_transaksi_besar
        ]

        # Assert adalah pemeriksaan internal sesudah proses hitung, bukan validasi input.
        assert total >= Decimal("0"), "Total transaksi tidak mungkin negatif."

        return {
            "jumlah": len(self.transaksi),
            "total": total,
            "rata_rata": self.rata_rata(),
            "batas_transaksi_besar": batas_transaksi_besar,
            "jumlah_transaksi_besar": len(transaksi_besar),
            "transaksi_besar": transaksi_besar,
            "per_kategori": self.per_kategori(),
        }


if __name__ == "__main__":
    # Pengujian lokal modul tanpa bergantung pada file data aplikasi.
    from decimal import Decimal

    assert hitung_total(Decimal("12000"), Decimal("8000")) == Decimal("20000")
    print("Pengujian lokal processing berhasil.")
