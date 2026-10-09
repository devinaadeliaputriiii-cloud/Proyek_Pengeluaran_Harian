"""Penyimpanan transaksi JSON Lines dengan seluruh mode file yang diminta."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import Transaksi


@dataclass
class HasilBaca:
    """Hasil pembacaan file termasuk jumlah baris rusak yang berhasil dilewati."""

    transaksi: list[Transaksi]
    baris_rusak: int = 0


class RepositoryTransaksi:
    """Mengisolasi operasi file agar menu tidak menangani format penyimpanan."""

    def __init__(self, file_data: Path | str) -> None:
        self.file_data = Path(file_data)

    def buat_file_pertama_kali(self) -> bool:
        """Membuat file kosong dengan mode x; file lama selalu dipertahankan."""
        self.file_data.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.file_data, "x", encoding="utf-8") as file:
                file.write("")
            return True
        except FileExistsError:
            return False

    def tambah(self, transaksi: Transaksi) -> None:
        """Menambah satu record memakai mode a tanpa menghapus transaksi sebelumnya."""
        self.buat_file_pertama_kali()
        with open(self.file_data, "a", encoding="utf-8") as file:
            file.write(json.dumps(transaksi.ke_record(), ensure_ascii=False) + "\n")

    def baca(self) -> HasilBaca:
        """Membaca iteratif dengan mode r dan melewati record rusak secara aman."""
        transaksi: list[Transaksi] = []
        baris_rusak = 0
        try:
            with open(self.file_data, "r", encoding="utf-8") as file:
                for nomor_baris, baris in enumerate(file, start=1):
                    if not baris.strip():
                        continue
                    try:
                        record = json.loads(baris)
                        transaksi.append(Transaksi.dari_record(record))
                    except (json.JSONDecodeError, TypeError, ValueError) as error:
                        # Baris rusak tidak mematikan aplikasi; catat jumlahnya untuk pengguna.
                        baris_rusak += 1
                        print(f"Peringatan: baris data rusak ke-{nomor_baris} dilewati ({error}).")
        except FileNotFoundError:
            # Pemulihan aman: buat file baru kosong dan lanjutkan dengan data kosong.
            print(f"File data belum tersedia: {self.file_data}. File baru dibuat.")
            self.buat_file_pertama_kali()
        return HasilBaca(transaksi=transaksi, baris_rusak=baris_rusak)

    def simpan_semua(self, transaksi: Iterable[Transaksi]) -> None:
        """Menulis ulang dataset dengan mode w, dipakai sesudah penghapusan terkonfirmasi."""
        self.buat_file_pertama_kali()
        with open(self.file_data, "w", encoding="utf-8") as file:
            for item in transaksi:
                file.write(json.dumps(item.ke_record(), ensure_ascii=False) + "\n")

    def hapus_berdasarkan_id(self, id_transaksi: str) -> Transaksi | None:
        """Menghapus satu transaksi, lalu memperbarui file hanya bila ID ditemukan."""
        hasil = self.baca()
        target = next(
            (item for item in hasil.transaksi if item.id.casefold() == id_transaksi.strip().casefold()),
            None,
        )
        if target is None:
            return None
        sisa = [item for item in hasil.transaksi if item.id != target.id]
        self.simpan_semua(sisa)
        return target


if __name__ == "__main__":
    # Uji lokal memakai folder sementara agar data pengguna tidak tersentuh.
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as folder:
        repo = RepositoryTransaksi(Path(folder) / "uji.jsonl")
        assert repo.buat_file_pertama_kali() is True
        assert repo.buat_file_pertama_kali() is False
        print("Pengujian lokal fileio berhasil.")
