# Proyek Pengeluaran Harian

Aplikasi terminal Python untuk mencatat pengeluaran pribadi. Pengguna dapat
menambahkan, menampilkan, menganalisis, mencari, menghapus, dan melaporkan
transaksi yang benar-benar dimasukkan sendiri.

## Fitur
- Tambah transaksi dengan validasi tanggal, kategori, dan nominal.
- Tampilkan seluruh transaksi beserta ID untuk penghapusan.
- Ringkasan jumlah, total, rata-rata, transaksi besar, kategori, dan urutan nominal.
- Pencarian kata kunci pada tanggal, kategori, atau catatan.
- Penghapusan transaksi dengan konfirmasi ya.
- Laporan teks yang dapat dibuat ulang kapan saja.
- Baris data rusak dilewati tanpa menghentikan program.
- Pengujian otomatis menggunakan unittest.

## Struktur folder
Proyek_Pengeluaran_Harian
- main.py — menu interaktif aplikasi.
- keuangan/ — package utama.
  - __init__.py — penanda package dan ekspor utama.
  - models.py — class Transaksi dan BukuPengeluaran.
  - validasi.py — validasi input serta exception buatan.
  - processing.py — analisis, args, kwargs, dan lambda.
  - fileio.py — baca, tambah, dan tulis data JSON Lines.
  - laporan.py — penyusunan serta penulisan laporan.
- data/ — akan berisi transaksi.jsonl.
- laporan/ — akan berisi laporan_pengeluaran.txt.
- tests/test_pengeluaran.py — 12 pengujian unittest.
- REFACTORING.md, PEMERIKSAAN_AWAL.md, CHECKLIST_AKHIR.md.

## Menjalankan pengujian
Dari folder proyek jalankan: python -m unittest discover -s tests -v
Tes memakai folder sementara, sehingga tidak menghapus atau mengubah file
data transaksi pengguna.

## Penyimpanan data dan laporan
- Data transaksi: data/transaksi.jsonl
- Laporan terbaru: laporan/laporan_pengeluaran.txt




