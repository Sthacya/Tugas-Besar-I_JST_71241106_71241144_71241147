# TB1-JSTKelompokXX: Klasifikasi Kelayakan Mobil dengan Perceptron vs ADALINE

**Mata kuliah:** Jaringan Syaraf Tiruan (IT6053), FTI UKDW  
**Kasus:** Kelayakan beli mobil (*Car Evaluation*, UCI), kelanjutan Tugas 1. Dua kelas: **`unacc` (−1, tidak layak)** vs **`acc` (+1, layak, kelas positif)** dari 6 fitur kategorikal (21 kolom one-hot).

# Anggota dan kontribusi
| Nama | NIM | Kontribusi |
|---|---|---|
| Sthacya Marela Elsithalia Lakamola | 71241106 | implementasi Perceptron + hitungan manual|
| Sandy Rehan Linta' | 71241144 | implementasi ADALINE + eksperimen |
| Yosiabes Priarsono | 71241147 | visualisasi, laporan, presentasi |

# Struktur dan tautan berkas
| Berkas | Isi |
|---|---|
| [TB1_KelompokTrioMacan.ipynb](TB1_KelompokTrioMacan.ipynb) | Notebook lengkap: kode, penjelasan, hitungan manual, 8 pelatihan, hasil, diagnostik, pembahasan, lampiran |
| [TB1_KelompokTrioMacan.pdf](TB1_KelompokTrioMacan.pdf) | Laporan (isi utama 7 halaman, di luar sampul, daftar pustaka, dan lampiran) |
| [Presentasi_TB1.pdf](Presentasi_TB1.pdf) | Slide presentasi (7 slide) |
| [dataset.csv](dataset.csv) | Data yang dipakai eksperimen: 1594 baris (`unacc` 1210 + `acc` 384), 6 fitur + `class` |
| [car_evaluation_full.csv](car_evaluation_full.csv) | Dataset penuh 4 kelas (1728 baris), hanya untuk deskripsi |
| [scripts/rekonstruksi_car_evaluation.py](scripts/rekonstruksi_car_evaluation.py) | Skrip pembentuk `car_evaluation_full.csv` dari tabel aturan DEX |
| [scripts/verifikasi_car_data.py](scripts/verifikasi_car_data.py) | Membandingkan berkas data dengan `car.data` asli UCI baris per baris |
| [scripts/bangun_pdf.py](scripts/bangun_pdf.py) | (Opsional) membuat ulang laporan dan slide PDF dari `results/` dan `figures/` |
| [requirements.txt](requirements.txt) | Dependensi dan versi untuk menjalankan notebook |
| [figures/](figures/), [results/](results/) | Gambar dan tabel CSV hasil (ditulis ulang oleh notebook) |

# Data
* **Sumber:** UCI *Car Evaluation* (Bohanec & Rajkovic; 1997), https://archive.ics.uci.edu/dataset/19/car+evaluation, **CC BY 4.0**. Tidak ada data pribadi. Label berasal dari model keputusan pakar DEX, bukan survei pembeli.
* **Asal berkas:** `car_evaluation_full.csv` dibentuk dari tabel aturan DEX yang dipublikasikan (dataset mencakup seluruh 1728 kombinasi atribut; label deterministik) dan cocok dengan distribusi kelas resmi (1210/384/69/65). Untuk membuktikan bahwa isinya identik dengan data asli, unduh `car.data` dari UCI lalu jalankan dari direktori utama repo:
  ```bash
  python scripts/verifikasi_car_data.py path/ke/car.data
  ```
  **Hasil verifikasi kelompok: ISI:** (tulis `IDENTIK` atau uraikan perbedaannya; jika berbeda, ganti `car_evaluation_full.csv` dan `dataset.csv` dengan data asli dan jalankan ulang notebook).
* **Kolom:** `buying` {vhigh, high, med, low}, `maint` {vhigh, high, med, low}, `doors` {2, 3, 4, 5more}, `persons` {2, 4, more}, `lug_boot` {small, med, big}, `safety` {low, med, high}; target `class`.
* **Transformasi:** one-hot (6 fitur → 21 kolom 0/1); `acc` → +1, `unacc` → −1; tanpa missing value dan tanpa duplikat; standardisasi z-score memakai statistik data latih saja.
* **Pemilihan dua kelas:** dua kelas terbesar (cukup data; `good`/`vgood` hanya 69/65) dan sesuai inti kasus: layak vs tidak layak.
* **Split:** 80:20 berstratifikasi, `random_state = 42` (latih 1275, uji 319).

# Cara menjalankan
```bash
git clone https://github.com/Sthacya/Tugas-Besar-I_JST_71241106_71241144_71241147.git/<akun>/TB1-JSTKelompokXX.git      
cd TB1-JSTKelompokXX
python -m venv .venv && source .venv/bin/activate             
pip install -r requirements.txt
jupyter notebook TB1_KelompokTrioMacan.ipynb                          
```
Notebook membaca `dataset.csv` dan `car_evaluation_full.csv`, lalu menulis ulang `figures/` dan `results/`. Waktu eksekusi total ±25 detik.

**Versi:** Python 3.12.3 · NumPy 2.4.4 · pandas 3.0.2 · scikit-learn 1.8.0 · matplotlib 3.10.8 · SciPy 1.17.1 (hanya untuk uji keterpisahan linear) · Notebook 7.6.3 · **Seed 42**.

# Ringkasan hasil (data uji 319 sampel; baseline "selalu unacc" = 0,7586; semua 50 epoch)
| Model | η | Standardisasi | Akurasi latih | Akurasi uji | Precision / Recall / F1 (acc) | FP |
|---|---|---|---|---|---|---|
| Perceptron | 0,001 | Ya | 0,9200 | 0,9028 | 0,726 / 0,961 / 0,827 | 28 |
| Perceptron | 0,01 | Ya | 0,9200 | 0,9028 | 0,726 / 0,961 / 0,827 | 28 |
| Perceptron | 0,1 | Ya | 0,9200 | 0,9028 | 0,726 / 0,961 / 0,827 | 28 |
| ADALINE | 0,001 | Ya | 0,8988 | 0,8683 | 0,647 / 1,000 / 0,786 | 42 |
| ADALINE | 0,01 | Ya | 0,9169 | 0,8934 | 0,694 / 1,000 / 0,819 | 34 |
| ADALINE | 0,1 | Ya | 0,9412 | 0,9467 | 0,875 / 0,909 / 0,892 | 10 |
| Perceptron | 0,01 | Tidak | 0,9043 | 0,8746 | 0,658 / 1,000 / 0,794 | 40 |
| ADALINE | 0,01 | Tidak | 0,7592 | 0,7586 | 0,000 / 0,000 / 0,000 | 0 |

Temuan utama:
* Data latih **tidak terpisah linear**: uji pasti *linear programming* menyatakan *infeasible*; Perceptron tidak pernah mencapai nol pembaruan (minimum 89 dalam 2000 epoch).
* **η tidak mengubah Perceptron** (inisialisasi nol, urutan tetap: η hanya menskalakan bobot), tetapi sangat memengaruhi ADALINE; ADALINE η = 0,1 mencapai J = 0,1938 = J\* (solusi kuadrat terkecil).
* **Tanpa standardisasi ADALINE lebih lambat, bukan gagal**: pada 50 epoch hanya setara baseline, tetapi pada 3000 epoch (data latih) mencapai J\* yang sama (κ = 13,3 vs 1,67).
* Bobot one-hot tidak unik (matriks [X 1] berperingkat 16 dari 22), sehingga bobot ditafsirkan relatif dalam satu grup atribut.
* Detail, bukti, dan keterbatasan ada di notebook bagian 6–7, di laporan PDF, dan di Lampiran A (hitungan manual).

# Referensi
Lihat bagian 9 notebook dan daftar pustaka laporan (Bohanec & Rajkovic 1990; Zupan dkk. 1997; halaman dataset DEX; UCI; Rosenblatt 1958; Widrow & Hoff 1960; mlxtend Adaline).

# Bantuan AI
Claude (Anthropic) dan ChatGPT (OpenAI) digunakan untuk: menyusun kerangka notebook dan kode awal
Perceptron dan ADALINE, merekonstruksi berkas data, menyusun draf pembahasan, laporan PDF, dan slide,
serta merevisi hasil review. [ISI: peran ChatGPT]

Verifikasi yang kami lakukan (hanya tulis yang benar-benar dikerjakan):
- Menjalankan ulang seluruh notebook dari awal (Run All) dan hasilnya cocok dengan tabel.
- Menghitung ulang hitungan manual dengan tangan dan mencocokkannya dengan kode.
- Menjalankan scripts/verifikasi_car_data.py terhadap car.data dari UCI; hasil: [IDENTIK / uraikan].
- Memeriksa tautan sumber (UCI, Raschka, Widrow & Hoff, Rosenblatt) dan isi sitasi.
- Mempelajari kode dan siap menjelaskannya saat presentasi.

# Commit yang dinilai

