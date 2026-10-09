"""Model objek untuk data transaksi dan koleksi pengeluaran."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable
from uuid import uuid4

from .validasi import catatan_valid, nominal_valid, record_valid, tanggal_valid, teks_wajib


@dataclass
class Transaksi:
    """Satu pengeluaran pribadi yang dapat disimpan sebagai JSON Lines."""

    tanggal: str
    kategori: str
    nominal: Decimal
    catatan: str = ""
    id: str = field(default_factory=lambda: uuid4().hex[:10])

    def __post_init__(self) -> None:
        """Menjaga objek selalu valid, termasuk yang tidak berasal dari input menu."""
        data = record_valid(
            {
                "id": self.id,
                "tanggal": self.tanggal,
                "kategori": self.kategori,
                "nominal": self.nominal,
                "catatan": self.catatan,
            }
        )
        self.id = data["id"]
        self.tanggal = data["tanggal"]
        self.kategori = data["kategori"]
        self.nominal = data["nominal"]
        self.catatan = data["catatan"]

    def ke_record(self) -> dict[str, str]:
        """Mengubah objek ke record serialisasi yang konsisten."""
        return {
            "id": self.id,
            "tanggal": self.tanggal,
            "kategori": self.kategori,
            "nominal": str(self.nominal),
            "catatan": self.catatan,
        }

    @classmethod
    def dari_record(cls, record: dict[str, object]) -> "Transaksi":
        """Membuat objek Transaksi dari satu record yang sudah dibaca dari file."""
        data = record_valid(record)
        return cls(**data)

    def tampilkan(self) -> str:
        """Membuat satu baris teks yang nyaman dibaca pada menu dan laporan."""
        catatan = self.catatan if self.catatan else "-"
        return (
            f"[{self.id}] {self.tanggal} | {self.kategori} | "
            f"Rp{self.nominal:,.2f} | {catatan}"
        )


class BukuPengeluaran:
    """Koleksi transaksi yang menyimpan operasi data sederhana di satu tempat."""

    def __init__(self, transaksi: Iterable[Transaksi] = ()) -> None:
        self._transaksi = list(transaksi)

    def semua(self) -> list[Transaksi]:
        """Mengembalikan salinan daftar agar data internal tidak diubah dari luar."""
        return list(self._transaksi)

    def tambah(self, transaksi: Transaksi) -> None:
        """Menambah satu transaksi yang sudah tervalidasi."""
        if not isinstance(transaksi, Transaksi):
            raise TypeError("BukuPengeluaran hanya menerima objek Transaksi.")
        self._transaksi.append(transaksi)

    def cari_id(self, id_transaksi: str) -> Transaksi | None:
        """Mencari transaksi berdasarkan ID singkat yang ditampilkan ke pengguna."""
        id_bersih = str(id_transaksi).strip().lower()
        return next((item for item in self._transaksi if item.id.lower() == id_bersih), None)

    def hapus(self, id_transaksi: str) -> Transaksi | None:
        """Menghapus transaksi berdasarkan ID dan mengembalikan objek yang terhapus."""
        transaksi = self.cari_id(id_transaksi)
        if transaksi is not None:
            self._transaksi.remove(transaksi)
        return transaksi

    def jumlah(self) -> int:
        """Mengembalikan banyaknya transaksi yang sedang dikelola."""
        return len(self._transaksi)
