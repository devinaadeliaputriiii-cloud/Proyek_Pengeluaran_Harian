"""Fungsi pengolahan dan analisis transaksi."""


def hitung_total(*nominal):
    """Menjumlahkan nominal; *args menerima jumlah angka yang berbeda."""
    return sum(nominal)


def buat_transaksi(**data):
    """Membuat Transaksi dari atribut bervariasi melalui **kwargs."""
    from .models import Transaksi
    return Transaksi(
        data.get("tanggal", ""),
        data.get("kategori", "Lainnya"),
        data.get("nominal", 0),
        data.get("catatan", ""),
    )


def rata_rata(transaksi):
    """Menghitung rata-rata nominal atau nol bila daftar masih kosong."""
    if not transaksi:
        return 0
    return hitung_total(*(item.nominal for item in transaksi)) / len(transaksi)


def urutkan_transaksi(transaksi, menurun=True):
    """Mengurutkan data dengan lambda sebagai key berdasarkan nominal."""
    return sorted(transaksi, key=lambda item: item.nominal, reverse=menurun)


def buat_ringkasan(transaksi, batas_besar=100000):
    """Menganalisis jumlah, total, rata-rata, dan transaksi besar."""
    total = hitung_total(*(item.nominal for item in transaksi))
    besar = [item for item in transaksi if item.nominal >= batas_besar]
    return {
        "jumlah": len(transaksi),
        "total": total,
        "rata_rata": rata_rata(transaksi),
        "transaksi_besar": len(besar),
    }


if __name__ == "__main__":
    # Pengujian lokal modul processing tanpa menjalankan main.py.
    assert hitung_total(1000, 2000) == 3000
    print("Pengujian lokal processing berhasil.")
