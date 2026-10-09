"""Program menu interaktif untuk pencatatan pengeluaran pribadi."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from keuangan.fileio import RepositoryTransaksi
from keuangan.laporan import susun_laporan, tulis_laporan
from keuangan.processing import AnalisisPengeluaran, buat_transaksi
from keuangan.validasi import DataTransaksiError, nominal_valid, tanggal_valid, teks_wajib


ROOT_DIR = Path(__file__).resolve().parent
DATA_FILE = ROOT_DIR / "data" / "transaksi.jsonl"
LAPORAN_FILE = ROOT_DIR / "laporan" / "laporan_pengeluaran.txt"
BATAS_DEFAULT = Decimal("100000")


def cetak_judul(judul: str) -> None:
    """Mencetak pemisah sederhana agar menu terminal mudah dibaca."""
    print("\n" + "=" * 56)
    print(judul)
    print("=" * 56)


def muat_transaksi(repository: RepositoryTransaksi):
    """Memuat transaksi dan memberi tahu pengguna jika ada record rusak."""
    hasil = repository.baca()
    if hasil.baris_rusak:
        print(f"{hasil.baris_rusak} baris rusak dilewati dengan aman.")
    return hasil.transaksi


def input_batas() -> Decimal:
    """Membaca batas transaksi besar dengan nilai default saat Enter ditekan."""
    nilai = input(f"Batas transaksi besar [default {BATAS_DEFAULT}]: ").strip()
    if not nilai:
        return BATAS_DEFAULT
    return nominal_valid(nilai)


def tambah_transaksi(repository: RepositoryTransaksi) -> None:
    """Meminta input transaksi, memvalidasi, lalu menyimpannya secara permanen."""
    cetak_judul("TAMBAH TRANSAKSI")
    try:
        tanggal = tanggal_valid(input("Tanggal (YYYY-MM-DD): "))
        kategori = teks_wajib(input("Kategori: "), "Kategori")
        nominal = nominal_valid(input("Nominal: "))
        catatan = input("Catatan (boleh kosong): ")

        # Pemanggilan dengan keyword argument memperjelas atribut tiap transaksi.
        transaksi = buat_transaksi(
            tanggal=tanggal,
            kategori=kategori,
            nominal=nominal,
            catatan=catatan,
        )
        repository.tambah(transaksi)
        print(f"Transaksi tersimpan dengan ID {transaksi.id}.")
    except DataTransaksiError as error:
        print(f"Data tidak disimpan: {error}")


def tampilkan_transaksi(repository: RepositoryTransaksi) -> None:
    """Menampilkan semua transaksi yang sudah tersimpan."""
    cetak_judul("SEMUA TRANSAKSI")
    transaksi = muat_transaksi(repository)
    if not transaksi:
        print("Belum ada transaksi. Gunakan menu 1 untuk menambah data.")
        return
    for nomor, item in enumerate(transaksi, start=1):
        print(f"{nomor}. {item.tampilkan()}")


def tampilkan_ringkasan(repository: RepositoryTransaksi) -> None:
    """Menampilkan metrik ringkas, transaksi besar, dan urutan nominal."""
    cetak_judul("RINGKASAN PENGELUARAN")
    transaksi = muat_transaksi(repository)
    try:
        batas = input_batas()
    except DataTransaksiError as error:
        print(f"Batas tidak valid: {error}")
        return

    analisis = AnalisisPengeluaran(transaksi)
    ringkasan = analisis.buat_ringkasan(batas_transaksi_besar=batas)
    print(f"Jumlah transaksi       : {ringkasan['jumlah']}")
    print(f"Total pengeluaran      : Rp{ringkasan['total']:,.2f}")
    print(f"Rata-rata pengeluaran  : Rp{ringkasan['rata_rata']:,.2f}")
    print(f"Transaksi >= Rp{batas:,.2f}: {ringkasan['jumlah_transaksi_besar']}")
    print("\nUrutan nominal terbesar:")
    for item in analisis.urutkan_nominal():
        print("-", item.tampilkan())


def cari_transaksi(repository: RepositoryTransaksi) -> None:
    """Mencari transaksi dari kata pada tanggal, kategori, ataupun catatan."""
    cetak_judul("CARI TRANSAKSI")
    kata = input("Kata kunci: ").strip()
    if not kata:
        print("Pencarian dibatalkan karena kata kunci kosong.")
        return
    hasil = AnalisisPengeluaran(muat_transaksi(repository)).cari(kata)
    if not hasil:
        print("Tidak ada transaksi yang cocok.")
        return
    print(f"Ditemukan {len(hasil)} transaksi:")
    for item in hasil:
        print("-", item.tampilkan())


def hapus_transaksi(repository: RepositoryTransaksi) -> None:
    """Menghapus transaksi hanya setelah ID dan konfirmasi pengguna sesuai."""
    cetak_judul("HAPUS TRANSAKSI")
    tampilkan_transaksi(repository)
    id_transaksi = input("\nMasukkan ID transaksi yang akan dihapus: ").strip()
    if not id_transaksi:
        print("Penghapusan dibatalkan.")
        return
    konfirmasi = input(f"Yakin hapus transaksi [{id_transaksi}]? (ya/tidak): ").strip().casefold()
    if konfirmasi != "ya":
        print("Penghapusan dibatalkan. Data tidak berubah.")
        return
    transaksi = repository.hapus_berdasarkan_id(id_transaksi)
    if transaksi is None:
        print("ID transaksi tidak ditemukan. Data tidak berubah.")
    else:
        print(f"Transaksi {transaksi.id} berhasil dihapus.")


def buat_laporan(repository: RepositoryTransaksi) -> None:
    """Menyusun ringkasan terbaru lalu menulisnya ke file laporan."""
    cetak_judul("BUAT / PERBARUI LAPORAN")
    try:
        batas = input_batas()
    except DataTransaksiError as error:
        print(f"Batas tidak valid: {error}")
        return
    analisis = AnalisisPengeluaran(muat_transaksi(repository))
    ringkasan = analisis.buat_ringkasan(batas_transaksi_besar=batas)
    isi = susun_laporan(ringkasan, analisis.urutkan_nominal())
    tujuan = tulis_laporan(LAPORAN_FILE, isi)
    print(f"Laporan berhasil disimpan di: {tujuan}")
    print("\n" + isi)


def tampilkan_menu() -> None:
    """Menampilkan pilihan menu utama aplikasi."""
    print(
        "\nMENU PENGELUARAN HARIAN\n"
        "1. Tambah transaksi\n"
        "2. Tampilkan seluruh transaksi\n"
        "3. Lihat ringkasan pengeluaran\n"
        "4. Cari transaksi\n"
        "5. Hapus transaksi (dengan konfirmasi)\n"
        "6. Buat / perbarui laporan\n"
        "7. Keluar"
    )


def jalankan_program() -> None:
    """Menjalankan loop menu sampai pengguna memilih keluar dengan aman."""
    repository = RepositoryTransaksi(DATA_FILE)
    repository.buat_file_pertama_kali()
    cetak_judul("APLIKASI PENGELUARAN HARIAN")
    print("Data tersimpan otomatis di folder data dan tidak dihapus saat program ditutup.")

    aksi = {
        "1": tambah_transaksi,
        "2": tampilkan_transaksi,
        "3": tampilkan_ringkasan,
        "4": cari_transaksi,
        "5": hapus_transaksi,
        "6": buat_laporan,
    }
    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu (1-7): ").strip()
        if pilihan == "7":
            print("Terima kasih. Semua data yang sudah tersimpan tetap aman.")
            break
        fungsi = aksi.get(pilihan)
        if fungsi is None:
            print("Pilihan tidak tersedia. Masukkan angka 1 sampai 7.")
            continue
        try:
            fungsi(repository)
        except (OSError, ValueError) as error:
            # Lapisan terakhir agar kesalahan input atau file tidak menghentikan menu.
            print(f"Terjadi masalah yang dapat ditangani: {error}")


if __name__ == "__main__":
    jalankan_program()
