"""Class data untuk program pengeluaran harian."""


class Transaksi:
    """Mewakili satu catatan pengeluaran."""

    def __init__(self, tanggal, kategori, nominal, catatan=""):
        self.tanggal = tanggal
        self.kategori = kategori
        self.nominal = float(nominal)
        self.catatan = catatan

    def ke_baris_file(self):
        """Mengubah objek transaksi menjadi format teks untuk file."""
        return f"{self.tanggal};{self.kategori};{self.nominal};{self.catatan}"

    def tampilkan(self):
        """Mengembalikan teks transaksi yang mudah dibaca."""
        return f"{self.tanggal} | {self.kategori} | Rp{self.nominal:,.0f} | {self.catatan}"


class BukuKeuangan:
    """Menyimpan kumpulan transaksi dan menyediakan operasi sederhana."""

    def __init__(self):
        self.transaksi = []

    def tambah(self, transaksi):
        """Menambahkan satu objek Transaksi ke daftar."""
        self.transaksi.append(transaksi)

    def jumlah_transaksi(self):
        """Mengembalikan jumlah data transaksi."""
        return len(self.transaksi)

    def total(self):
        """Menghitung total semua nominal dengan *args melalui processing."""
        from .processing import hitung_total
        return hitung_total(*(item.nominal for item in self.transaksi))
