"""Membangun laporan (TB1_KelompokXX.pdf) dan slide (Presentasi_TB1.pdf) dari hasil notebook.

OPSIONAL (hanya untuk membuat ulang PDF; notebook tidak membutuhkannya):
    pip install -r scripts/requirements-pdf.txt
    python scripts/bangun_pdf.py            # jalankan dari direktori utama repo, setelah notebook dijalankan

Ubah GROUP di bawah ini (mis. "07") lalu jalankan ulang untuk memperbarui sampul dan nama berkas.
Semua angka tabel dibaca dari results/*.csv; gambar dari figures/.
"""
import os
import numpy as np, pandas as pd
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
                                PageBreak, KeepTogether)

GROUP = "XX"                      # <- ganti dengan nomor kelompok
ANGGOTA = [("Sthacya Marela Elsithalia Lakamola", "71241106"),
           ("Sandy Rehan Linta'", "71241144"),
           ("Yosiabes Priarsono", "71241147")]
FD = "/usr/share/fonts/truetype/dejavu/"
for n, f in (("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"), ("DV-I", "DejaVuSans-Oblique.ttf"),
             ("DV-BI", "DejaVuSans-BoldOblique.ttf"), ("DVM", "DejaVuSansMono.ttf")):
    pdfmetrics.registerFont(TTFont(n, FD + f))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

NAVY, TEAL, LIGHT, GRID = colors.HexColor("#1F3A5F"), colors.HexColor("#2E7D6B"), colors.HexColor("#EEF3F8"), colors.HexColor("#B8C4D0")
R = lambda p: pd.read_csv(os.path.join("results", p))

# ----------------------------------------------------------------------------------- data dari hasil notebook
hk = R("hasil_konfigurasi.csv"); mk = R("metrik_kelas_positif.csv"); dg = R("diagnostik_adaline_raw_vs_std.csv")
rw = pd.read_csv("results/riwayat_epoch_10_30_50.csv", header=None, skiprows=3)
bw = pd.read_csv("results/bobot_bias_akhir.csv", index_col=0)
f2 = lambda v, d=4: f"{v:.{d}f}".replace(".", ",")
STD = lambda v: "Ya" if v == "Ya" else "Tidak"

# ----------------------------------------------------------------------------------- gaya
S = dict(
    body=ParagraphStyle("b", fontName="DV", fontSize=9, leading=12.6, alignment=TA_JUSTIFY, spaceAfter=4),
    h1=ParagraphStyle("h1", fontName="DV-B", fontSize=12, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=4, keepWithNext=1),
    h2=ParagraphStyle("h2", fontName="DV-B", fontSize=9.6, leading=12.5, textColor=TEAL, spaceBefore=5, spaceAfter=2, keepWithNext=1),
    cap=ParagraphStyle("c", fontName="DV-I", fontSize=7.8, leading=10, textColor=colors.HexColor("#444444"), spaceAfter=6),
    cell=ParagraphStyle("t", fontName="DV", fontSize=7.8, leading=10),
    cellb=ParagraphStyle("tb", fontName="DV-B", fontSize=7.8, leading=10, textColor=colors.white),
    bul=ParagraphStyle("bu", fontName="DV", fontSize=9, leading=12.4, leftIndent=12, bulletIndent=2, alignment=TA_JUSTIFY, spaceAfter=2),
    mono=ParagraphStyle("m", fontName="DVM", fontSize=8.2, leading=11, leftIndent=8, spaceAfter=3, textColor=colors.HexColor("#222222")),
)
P = lambda t, s="body": Paragraph(t, S[s])
B = lambda t: Paragraph(t, S["bul"], bulletText="•")

def tbl(rows, widths, head=True, fs=None, zebra=True):
    data = [[Paragraph(str(c), S["cellb"] if (head and i == 0) else S["cell"]) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    st = [("GRID", (0, 0), (-1, -1), .4, GRID), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2)]
    if head: st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1 if head else 0, len(rows)):
            if i % 2 == 0: st.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(st)); return t

def fig(path, width_cm, caption):
    w, h = PILImage.open(path).size
    im = Image(path, width=width_cm * cm, height=width_cm * cm * h / w)
    return KeepTogether([im, P(caption, "cap")])

def footer(c, d):
    c.saveState(); c.setFont("DV", 7.5); c.setFillColor(colors.HexColor("#666666"))
    c.drawString(2 * cm, 1.1 * cm, f"TB1 Jaringan Syaraf Tiruan (IT6053) · Kelompok {GROUP}")
    c.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Halaman {d.page}"); c.restoreState()

def cover(c, d):
    c.saveState(); W, H = A4
    c.setFillColor(NAVY); c.rect(0, H - 4.2 * cm, W, 4.2 * cm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("DV-B", 11); c.drawString(2.2 * cm, H - 2.2 * cm, "FTI UKDW  |  JARINGAN SYARAF TIRUAN  |  IT6053")
    c.setFont("DV", 9.5); c.drawString(2.2 * cm, H - 3.2 * cm, "Tugas Besar 1 · Laporan")
    c.setFillColor(NAVY); c.setFont("DV-B", 20)
    for k, ln in enumerate(["Klasifikasi Kelayakan Mobil", "dengan Perceptron dan ADALINE"]):
        c.drawString(2.2 * cm, H - 8.2 * cm - k * 1.0 * cm, ln)
    c.setFillColor(colors.HexColor("#444444")); c.setFont("DV", 10.5)
    c.drawString(2.2 * cm, H - 10.9 * cm, "Studi kasus Car Evaluation (UCI): kelanjutan Tugas 1")
    c.setFont("DV-B", 11); c.setFillColor(TEAL); c.drawString(2.2 * cm, H - 13.2 * cm, f"Kelompok {GROUP}")
    c.setFillColor(colors.HexColor("#222222"))
    for k, (n, nim) in enumerate(ANGGOTA):
        c.setFont("DV", 10.5); c.drawString(2.2 * cm, H - 14.4 * cm - k * .8 * cm, f"{n}  ({nim})")
    c.setFont("DV", 9); c.setFillColor(colors.HexColor("#666666"))
    c.drawString(2.2 * cm, 3.0 * cm, "Repository: TB1-JSTKelompok" + GROUP + "  ·  Python 3.12.3, NumPy 2.4.4, seed 42")
    c.drawString(2.2 * cm, 2.4 * cm, "Oktober 2026"); c.restoreState()

# ----------------------------------------------------------------------------------- isi laporan
def laporan():
    st = []
    st += [PageBreak()]
    st += [P("1. Masalah dan tujuan", "h1"),
           P("Pada Tugas 1 kelompok merumuskan kasus <i>apakah sebuah mobil layak dipilih calon pembeli berdasarkan enam kriteria</i> "
             "(harga beli, biaya perawatan, jumlah pintu, kapasitas penumpang, ukuran bagasi, keselamatan) sebagai <b>supervised learning</b> "
             "klasifikasi empat kelas dengan MLP. Pada TB1 kasus itu dipersempit menjadi <b>klasifikasi dua kelas</b> dengan neuron tunggal: "
             "masukan <b>x</b> ∈ ℝ<super>21</super> (6 fitur kategorikal dalam bentuk one-hot), target y ∈ {−1, +1}, kelas positif (+1) = <b>acc</b> (layak), "
             "kelas negatif (−1) = <b>unacc</b> (tidak layak)."),
           P("<b>Tujuan:</b> (1) mengimplementasikan Perceptron dan ADALINE (Delta Rule) sendiri dengan NumPy; (2) membandingkan proses belajar keduanya "
             "pada delapan konfigurasi terkendali (η dan standardisasi); (3) menilai indikasi keterpisahan linear data; (4) menjelaskan hasil berdasarkan bukti, "
             "bukan hanya akurasi. Seperti pada Tugas 1, kesalahan paling berbahaya ialah <b>mobil tidak layak diprediksi layak</b>, yaitu <i>false positive</i> kelas acc; "
             "karena itu precision kelas positif dilaporkan di samping recall dan F1.")]

    st += [P("2. Dataset dan kaitannya dengan Tugas 1", "h1"),
           tbl([["Aspek", "Keterangan"],
                ["Sumber dan izin", "UCI Machine Learning Repository, <i>Car Evaluation</i> (Bohanec &amp; Rajkovic; didonasikan 1997); lisensi CC BY 4.0. Tidak ada data pribadi."],
                ["Asal label", "Model keputusan hierarkis DEX (aturan pakar), bukan survei pembeli sungguhan."],
                ["Observasi", "1.728 data penuh (seluruh 4·4·4·3·3·3 kombinasi atribut); <b>1.594</b> dipakai (unacc 1.210 + acc 384)."],
                ["Fitur (6, kategorikal)", "buying {vhigh, high, med, low}; maint {vhigh, high, med, low}; doors {2, 3, 4, 5more}; persons {2, 4, more}; lug_boot {small, med, big}; safety {low, med, high}."],
                ["Label dan distribusi", "acc → +1 (24,1%), unacc → −1 (75,9%). Baseline “selalu unacc” = 0,7586. Kelas timpang, sehingga precision, recall, dan F1 kelas positif dilaporkan."],
                ["Missing value, duplikasi", "Tidak ada missing value; tidak ada baris duplikat, sehingga imputasi tidak diperlukan."],
                ["Transformasi", "One-hot: 6 fitur → 21 kolom 0/1 (sama seperti Tugas 1); standardisasi z-score dari data latih saja."]],
               [3.4 * cm, 13.6 * cm]),
           Spacer(1, 4),
           P("<b>Pemilihan dua kelas.</b> Dipakai unacc vs acc karena (i) keduanya kelas terbesar sehingga data cukup (1.594 ≥ 100); (ii) good (69) dan vgood (65) terlalu sedikit "
             "(pada Tugas 1 hanya ±10 sampel di data uji sehingga metriknya tidak stabil); (iii) keputusan inti kasus ini ialah layak atau tidak layak dibeli. "
             "Konsekuensinya, eksperimen ini <b>bukan</b> masalah empat kelas penuh. <b>Yang dipertahankan dari Tugas 1:</b> dataset, enam fitur, one-hot 21 kolom, split berstrata, perhatian pada kelas timpang. "
             "<b>Yang berubah:</b> model (MLP softmax → neuron tunggal), kelas (4 → 2), split 70/15/15 → 80:20 (TB1 tidak memilih model sehingga tidak memerlukan data validasi)."),
           P("<b>Catatan asal berkas.</b> Berkas data dibentuk dari tabel aturan DEX yang dipublikasikan dan dicocokkan dengan <code>car.data</code> asli UCI memakai "
             "<code>scripts/verifikasi_car_data.py</code>; hasil verifikasi dicatat pada README repository.")]

    st += [P("3. Artikel dan kode pendukung", "h1"),
           tbl([["Sumber", "Jenis", "Kontribusi / adaptasi"],
                ["Bohanec &amp; Rajkovic (1990), <i>Expert system for decision making</i>", "Artikel (kasus)", "Asal dataset: label dari aturan bertingkat DEX (harga → teknis → kelayakan), sehingga hubungan fitur–label tidak diharapkan sepenuhnya aditif. Ini diuji (bagian 6 dan 7), bukan diasumsikan."],
                ["Zupan dkk. (1997), <i>Machine learning by function decomposition</i>", "Artikel (kasus)", "Menunjukkan model hierarkis dapat direkonstruksi sepenuhnya: data deterministik, tanpa derau, sehingga galat model linear mencerminkan keterbatasan kapasitas model. Hanya konteks; model utama tetap Perceptron dan ADALINE."],
                ["Rosenblatt (1958); Widrow &amp; Hoff (1960)", "Artikel (metode)", "Dasar aturan Perceptron dan Delta Rule / LMS."],
                ["Raschka, <i>Adaline</i> (dokumentasi mlxtend)", "Dokumentasi kode", "<b>Diadaptasi:</b> pola batch gradient descent (e = y − z; w += η·Xᵀe/n). <b>Diubah:</b> pembaruan bias mengikuti panduan; J = (1/2n)Σe² (bukan SSE); berhenti bila J inf/NaN dengan epoch dicatat; riwayat bobot dan akurasi per epoch. mlxtend tidak dipakai untuk pelatihan."]],
               [5.0 * cm, 2.6 * cm, 9.4 * cm])]

    st += [P("4. Model neuron dan aturan pembelajaran", "h1"),
           P("Kedua model memakai neuron z = w<super>T</super>x + b dan keputusan ŷ = +1 jika z ≥ 0, ŷ = −1 jika z &lt; 0. Bobot <b>w</b> menentukan arah batas keputusan "
             "(pada one-hot: satu bobot per nilai atribut), bias <b>b</b> menggeser hyperplane w<super>T</super>x + b = 0, dan η adalah laju belajar. "
             "Inisialisasi w = 0, b = 0; urutan sampel tetap seperti pada data latih (tanpa <i>shuffle</i>); 50 epoch."),
           tbl([["", "Perceptron (per sampel)", "ADALINE (batch, Delta Rule)"],
                ["Error", "Diskret: y − ŷ ∈ {0, ±2}", "Kontinu dari keluaran linear: e = y − z"],
                ["Pembaruan", "Δ = η(y − ŷ); w ← w + Δx; b ← b + Δ", "w ← w + η·Xᵀe/n; b ← b + η·mean(e)"],
                ["Kapan bobot berubah", "Hanya pada sampel yang salah klasifikasi", "Setiap epoch, dari semua sampel (juga yang sudah benar tetapi |z| &lt; 1)"],
                ["Fungsi objektif", "Tidak ada; dicatat jumlah pembaruan salah per epoch", "J = (1/2n)Σ(yᵢ − zᵢ)²; MSE = 2J; dicatat <i>sesudah</i> pembaruan di akhir epoch"],
                ["Ambang kelas", "Dipakai saat belajar dan prediksi", "Hanya saat prediksi"]],
               [3.0 * cm, 6.8 * cm, 7.2 * cm]),
           Spacer(1, 4),
           P("<b>Perhitungan manual.</b> Dua langkah pembaruan Perceptron dan dua iterasi batch ADALINE dihitung tangan pada data mini (Lampiran A) dan pada dua sampel data mobil nyata (Lampiran B); "
             "keduanya diperiksa dengan <code>assert</code> terhadap kelas <code>Perceptron</code> dan <code>Adaline</code> di notebook. "
             "Bobot dan bias akhir hitungan manual data mini: Perceptron w = (0,2; −0,2), b = 0; ADALINE w = (0,139375; −0,053125), b = −0,005.")]

    st += [P("5. Penyiapan data dan rancangan eksperimen", "h1"),
           B("<b>Split:</b> 80:20 berstratifikasi, <code>random_state = 42</code>: latih 1.275 (+1: 307, −1: 968), uji 319 (+1: 77, −1: 242). Split yang sama untuk semua model dan konfigurasi."),
           B("<b>Tanpa kebocoran:</b> mean dan simpangan baku standardisasi dipelajari hanya dari data latih. Domain nilai atribut tetap (ditentukan definisi dataset), sehingga one-hot tidak membocorkan data."),
           B("<b>Konfigurasi ditetapkan sebelum evaluasi uji.</b> Data uji hanya untuk pelaporan; tidak ada pemilihan model atau η terbaik, sehingga data validasi tidak diperlukan. Diagnostik tambahan memakai data latih saja."),
           B("<b>Divergen:</b> bila J atau parameter ADALINE menjadi inf/NaN, pelatihan dihentikan dan epoch dicatat (tidak terjadi pada kedelapan pelatihan)."),
           Spacer(1, 3),
           tbl([["#", "Model", "η", "Epoch", "Standardisasi"]] +
               [[i + 1, r.Model, str(r["η"]).replace(".", ","), 50, STD(r.Standardisasi)] for i, r in hk.iterrows()],
               [1.0 * cm, 3.2 * cm, 2.2 * cm, 2.0 * cm, 3.4 * cm]),
           P("Tabel 1. Delapan pelatihan. Inisialisasi, urutan sampel, dan split dipertahankan agar pengaruh skala fitur dapat dibandingkan.", "cap")]

    # ---- hasil
    st += [P("6. Hasil", "h1"), P("6.1 Tabel seluruh konfigurasi", "h2")]
    rows = [["Model", "η", "Std", "Akurasi latih", "Akurasi uji", "Galat latih akhir", "Pembaruan ep-50 / J akhir (MSE = 2J)"]]
    for _, r in hk.iterrows():
        last = f"{int(r['Pembaruan epoch-50'])} pembaruan" if r.Model == "Perceptron" else f"J = {f2(r['J akhir'])} (MSE {f2(r['MSE akhir'])})"
        rows.append([r.Model, str(r["η"]).replace(".", ","), STD(r.Standardisasi), f2(r["Akurasi latih"]), f2(r["Akurasi uji"]), f2(r["Galat latih akhir"]), last])
    st += [tbl(rows, [2.2 * cm, 1.4 * cm, 1.3 * cm, 2.2 * cm, 2.1 * cm, 2.6 * cm, 5.2 * cm]),
           P("Tabel 2. Akurasi memakai keluaran ambang. Baseline “selalu unacc” pada data uji = 0,7586. J ADALINE dicatat sesudah pembaruan epoch ke-50.", "cap"),
           P("6.2 Kondisi pada epoch ke-10, ke-30, dan ke-50", "h2")]
    rows = [["Konfigurasi", "Pembaruan salah / J (ep 10)", "(ep 30)", "(ep 50)", "Akurasi latih (ep 10)", "(ep 30)", "(ep 50)"]]
    for _, r in rw.iterrows():
        isp = r[0].startswith("Perceptron")
        v = [(f"{int(x)}" if isp else f2(x)) for x in r[1:4]]
        rows.append([r[0].replace("η=", "η = ").replace("std", "std.").replace("raw", "tanpa std.")] + v + [f2(x) for x in r[4:7]])
    st += [tbl(rows, [4.2 * cm, 2.6 * cm, 1.6 * cm, 1.6 * cm, 2.8 * cm, 1.8 * cm, 1.8 * cm]),
           P("Tabel 3. Perceptron: jumlah pembaruan salah pada epoch tersebut; ADALINE: J sesudah pembaruan.", "cap"),
           P("6.3 Confusion matrix, precision, recall, F1 (kelas positif = acc)", "h2")]
    rows = [["Konfigurasi", "TP", "FN", "FP", "TN", "Precision", "Recall", "F1"]]
    for _, r in mk.iterrows():
        rows.append([r.Konfigurasi.replace("η=", "η = ").replace(" std", " std.").replace(" raw", " tanpa std."), r.TP, r.FN, r.FP, r.TN, f2(r["Precision (+1)"], 3), f2(r["Recall (+1)"], 3), f2(r["F1 (+1)"], 3)])
    st += [tbl(rows, [4.8 * cm, 1.1 * cm, 1.1 * cm, 1.1 * cm, 1.2 * cm, 2.2 * cm, 2.0 * cm, 1.9 * cm]),
           P("Tabel 4. Urutan label [+1 (acc), −1 (unacc)]; baris = aktual, kolom = prediksi. TP = acc terdeteksi, FN = acc terlewat, <b>FP = unacc dikira acc (kesalahan berbahaya)</b>, TN = unacc benar.", "cap"),
           fig("figures/confusion_matrix_8_konfigurasi.png", 16.6, "Gambar 1. Confusion matrix data uji untuk delapan konfigurasi (urutan label +1 (acc), −1 (unacc))."),
           P("6.4 Kurva pelatihan dan kesalahan latih akhir", "h2"),
           fig("figures/kurva_perceptron.png", 16.6, "Gambar 2. Jumlah pembaruan salah klasifikasi per epoch (Perceptron). Tiga η terstandardisasi menghasilkan kurva identik."),
           fig("figures/kurva_adaline.png", 16.6, "Gambar 3. J per epoch (ADALINE): skala log dan linear untuk tiga η, serta perbandingan η = 0,01 tanpa dan dengan standardisasi."),
           P("Kesalahan latih setelah epoch terakhir (1 − akurasi latih): Perceptron 0,0800 (η = 0,001; 0,01; 0,1, standardisasi) dan 0,0957 (tanpa standardisasi); "
             "ADALINE 0,1012; 0,0831; 0,0588 (η = 0,001; 0,01; 0,1, standardisasi) dan 0,2408 (tanpa standardisasi).")]
    nrm = {c: float(np.linalg.norm(bw[c].iloc[:-1])) for c in bw.columns}
    rows = [["Konfigurasi", "‖w‖₂", "Bias b"]] + [[c.replace("η=", "η = ").replace(" std", " std.").replace(" raw", " tanpa std."), f2(nrm[c]), f2(bw[c].iloc[-1])] for c in bw.columns]
    st += [P("6.5 Bobot dan bias akhir", "h2"),
           tbl(rows, [6.0 * cm, 2.8 * cm, 2.8 * cm]),
           P("Tabel 5. Norma bobot dan bias akhir semua konfigurasi; 21 bobot per konfigurasi pada Lampiran C dan <code>results/bobot_bias_akhir.csv</code>.", "cap"),
           P("Dengan 21 fitur one-hot, batas keputusan adalah hyperplane berdimensi 20 dan tidak dapat digambar pada dua fitur (fitur biner hanya membentuk beberapa titik). "
             "Proyeksi yang setia adalah <b>skor z = w<super>T</super>x + b</b>, karena batas keputusan tepat berada di z = 0.")
           , fig("figures/skor_dan_bobot.png", 16.6, "Gambar 4. Histogram skor z data latih per kelas (batas keputusan di z = 0, sumbu vertikal skala log) dan bobot ADALINE η = 0,01 per nilai atribut."),
           fig("figures/diagnostik_perceptron_2000_epoch.png", 9.0, "Gambar 5. Diagnostik: Perceptron 2.000 epoch pada data latih terstandardisasi; jumlah pembaruan tidak pernah mencapai nol."),
           fig("figures/adaline_tanpa_standardisasi_3000_epoch.png", 15.0, "Gambar 6. Diagnostik: ADALINE η = 0,01 sampai 3.000 epoch, tanpa dan dengan standardisasi (hanya data latih).")]

    # ---- pembahasan
    st += [P("7. Pembahasan dan keterbatasan", "h1"),
           P("<b>(a) Keterpisahan linear.</b> Data <b>tidak</b> menunjukkan keterpisahan linear. Uji pasti dengan <i>linear programming</i> (mencari w, b dengan yᵢ(w<super>T</super>xᵢ + b) ≥ 1 untuk semua sampel latih) menyatakan sistem <i>infeasible</i>. "
             "Perilaku pelatihan konsisten: pada 2.000 epoch Perceptron tidak pernah mencapai nol pembaruan (minimum 89 pada epoch 29; 97 pada epoch 50 dan epoch 2.000; akurasi latih tertinggi ±0,94), sehingga teorema konvergensi Perceptron tidak berlaku. "
             "Histogram skor memperlihatkan kedua kelas tumpang tindih di sekitar z = 0. Bobot terbesar (persons=2 dan safety=low sangat negatif) sejalan dengan aturan pakar yang membuat dua kondisi itu selalu menghasilkan unacc (aturan “veto” yang dapat didekati secara linear), "
             "sedangkan syarat acc yang melibatkan kombinasi harga dan teknis tidak dapat ditangkap sempurna. Bagian terakhir ini adalah <i>interpretasi</i> kelompok; yang dibuktikan hanyalah ketidakterpisahan."),
           P("<b>(b) Perbedaan error.</b> Perceptron memakai error diskret y − ŷ ∈ {0, ±2}: bobot berubah hanya pada sampel yang salah, dengan langkah yang tidak bergantung pada jarak sampel ke batas. "
             "ADALINE memakai error kontinu e = y − z pada <i>semua</i> sampel, sehingga meminimalkan J. Pada η = 0,1, J turun dari 0,500 ke 0,222 (epoch 10), 0,194 (epoch 30), dan 0,1938 (epoch 50), "
             "sama dengan J<super>*</super> kuadrat terkecil (0,1938): ADALINE telah mencapai optimumnya. Jumlah kesalahan Perceptron berfluktuasi (163 pada epoch 1; 96; 97; 97) karena tidak ada fungsi objektif yang dijamin turun. "
             "J minimal tidak otomatis meminimalkan kesalahan klasifikasi."),
           P("<b>(c) Pengaruh η, epoch, dan standardisasi.</b>"),
           B("<b>η pada Perceptron: hasil identik.</b> Ketiga η menghasilkan 97 pembaruan, akurasi latih 0,9200, akurasi uji 0,9028, dan confusion matrix sama. Sebabnya inisialisasi nol, urutan tetap, dan η konstan positif: η hanya menskalakan w dan b "
             "(rasio w(η = 0,01)/w(η = 0,001) = 10 dan w(η = 0,1)/w(η = 0,001) = 100; ‖w‖ = 0,097 / 0,97 / 9,7), sehingga tanda z dan semua prediksi tidak berubah. Ini sah, bukan galat kode."),
           B("<b>η pada ADALINE: berpengaruh besar.</b> J epoch 50 = 0,466 / 0,290 / 0,194 dan akurasi uji 0,868 / 0,893 / 0,947 untuk η = 0,001 / 0,01 / 0,1. Dua η kecil belum konvergen pada epoch 50 (J masih turun; J<super>*</super> = 0,194). "
             "Semua η berada di bawah batas kestabilan 2/λ<sub>max</sub> = 1,20 (data standardisasi), sehingga tidak ada divergensi."),
           B("<b>Epoch.</b> Untuk ADALINE, epoch tambahan menurunkan J hingga J<super>*</super> (η = 0,1 tercapai sekitar epoch 30); untuk Perceptron, epoch tambahan tidak membantu."),
           B("<b>Standardisasi: mempercepat, bukan mengubah tujuan.</b> One-hot sudah berskala 0/1 sehingga tidak ada risiko ledakan; ADALINE tanpa standardisasi tidak divergen (η = 0,01 &lt; batas 0,725). Namun ia jauh lebih lambat karena kondisi numerik "
             "(κ = λ<sub>max</sub>/λ<sub>min</sub> = 13,3 tanpa vs 1,67 dengan standardisasi): pada epoch 50 akurasi latihnya 0,759 (sama dengan baseline) dan tidak pernah memprediksi acc. "
             "Diagnostik 3.000 epoch pada data latih (Gambar 6) menunjukkan model itu baru memprediksi acc pada epoch 240, mencapai J ≤ 1,01 J<super>*</super> pada epoch 841 (dengan standardisasi: epoch 230), "
             "dan akhirnya sampai ke J<super>*</super> dengan akurasi latih 0,9412, sama dengan model terstandardisasi. Pada Perceptron standardisasi mengubah bobot relatif antar kolom, sehingga hasil sedikit berbeda (akurasi uji 0,875 tanpa vs 0,903 dengan)."),
           P("<b>(d) Akurasi sama bukan berarti proses belajar sama.</b> ADALINE tanpa standardisasi memiliki akurasi uji 0,7586 (= baseline) padahal J-nya sudah turun dari 0,500 ke 0,328: ia belajar, tetapi keluaran ambangnya belum berbeda dari model trivial. "
             "Perceptron (akurasi uji 0,903; recall 0,961; precision 0,726; <b>28 FP</b>) dan ADALINE η = 0,1 (0,947; recall 0,909; precision 0,875; <b>10 FP</b>) juga memiliki profil kesalahan berbeda. "
             "Karena FP adalah kesalahan paling berbahaya pada kasus ini, profil kesalahan lebih penting daripada angka akurasi. ADALINE η = 0,1 terlihat terbaik pada data uji (17 salah vs 31 salah pada Perceptron), tetapi ini <b>laporan konfigurasi yang sudah ditetapkan, bukan hasil seleksi</b>, dan belum diuji secara statistik."),
           P("<b>(e) Kolinearitas one-hot.</b> Setiap grup one-hot berjumlah 1, sehingga kolom redundan dengan bias: matriks [X 1] hanya berperingkat 16 dari 22 kolom. Bobot karenanya tidak unik; nilai seperti persons=2 = −0,52 bermakna relatif terhadap bobot lain dalam grup yang sama. Prediksi dan J tidak terpengaruh."),
           P("<b>Keterbatasan.</b> (1) Satu split dan satu seed, tanpa validasi silang atau interval kepercayaan. (2) Data uji 319 sampel: satu sampel mengubah akurasi ±0,31 poin. "
             "(3) Dataset deterministik dan mencakup seluruh ruang atribut: data uji adalah kombinasi atribut yang tidak dipakai melatih, bukan sampel populasi mobil nyata, sehingga akurasi tidak boleh dibaca sebagai kinerja di dunia nyata. "
             "(4) Hanya dua dari empat kelas. (5) Model linear pada one-hot tidak dapat menyatakan interaksi antar atribut; keterbatasan ini inheren. (6) Inisialisasi nol dan urutan tetap; 50 epoch belum konvergen untuk ADALINE η kecil. "
             "(7) Akurasi latih tinggi tidak menjamin kinerja sempurna pada data baru. <b>Pengembangan:</b> fitur interaksi (mis. buying × maint) atau MLP seperti Tugas 1; validasi silang berstrata dan data validasi untuk memilih η dan epoch; "
             "penyesuaian ambang untuk menurunkan FP; perluasan ke empat kelas dengan one-vs-rest."),
           P("8. Kesimpulan", "h1"),
           B("Perceptron dan ADALINE berhasil diimplementasikan dengan NumPy untuk klasifikasi unacc vs acc (1.594 observasi, 21 fitur one-hot); hitungan manual dua langkah untuk keduanya cocok dengan kode."),
           B("Data latih <b>tidak terpisah linear</b> (linear programming infeasible; Perceptron tidak pernah mencapai nol kesalahan, minimum 89 pembaruan). Model linear pada one-hot tidak menangkap interaksi antar atribut, sehingga akurasi berada di sekitar 0,90–0,95."),
           B("Perceptron memperbarui bobot dari error diskret hanya saat salah; ADALINE dari error linear pada semua sampel dan konvergen mulus ke solusi kuadrat terkecil (η = 0,1: J = 0,1938 = J<super>*</super>). Pada data uji ADALINE η = 0,1 (akurasi 0,947; precision 0,875; recall 0,909) memiliki kesalahan berbahaya jauh lebih sedikit (FP = 10) daripada Perceptron (akurasi 0,903; FP = 28)."),
           B("η tidak mengubah hasil Perceptron (hanya skala bobot) tetapi menentukan kecepatan penurunan J pada ADALINE. Standardisasi tidak diperlukan untuk mencegah divergensi pada one-hot, tetapi mempercepat konvergensi: tanpa standardisasi ADALINE baru mencapai J<super>*</super> setelah ±1.000 epoch."),
           B("Akurasi yang sama tidak berarti proses belajar yang sama. Kesimpulan dibatasi oleh satu split, data deterministik, dan hanya dua kelas.")]

    # ---- daftar pustaka dan lampiran
    st += [PageBreak(), P("9. Daftar pustaka", "h1")]
    for t in ["Bohanec, M., &amp; Rajkovic, V. (1990). Expert system for decision making. <i>Sistemica</i>, 1(1), 145–157.",
              "Zupan, B., Bohanec, M., Bratko, I., &amp; Demšar, J. (1997). Machine learning by function decomposition. <i>Proc. ICML-97</i>, 421–429. https://file.biolab.si/biolab/blaz/papers/1997icml.pdf",
              "Bohanec, M., &amp; Zupan, B. <i>Car Dataset</i> (halaman dataset dan tabel aturan DEX). https://file.biolab.si/biolab/app/hint/car_dataset.html",
              "<i>Car Evaluation</i> [Dataset]. UCI Machine Learning Repository. https://archive.ics.uci.edu/dataset/19/car+evaluation (CC BY 4.0).",
              "Rosenblatt, F. (1958). The perceptron: A probabilistic model for information storage and organization in the brain. <i>Psychological Review</i>, 65(6), 386–408. https://doi.org/10.1037/h0042519",
              "Widrow, B., &amp; Hoff, M. E. (1960). Adaptive switching circuits. <i>IRE WESCON Convention Record</i>, Part 4, 96–104. https://isl.stanford.edu/~widrow/papers/c1960adaptiveswitching.pdf",
              "Raschka, S. (tanpa tahun). <i>Adaline: Adaptive Linear Neuron Classifier</i>. Dokumentasi mlxtend. https://rasbt.github.io/mlxtend/user_guide/classifier/Adaline/ (diakses 6 Oktober 2026)."]:
        st.append(P(t))
    st += [P("Lampiran A. Perhitungan manual pada data mini (η = 0,1, w = 0, b = 0)", "h1"),
           P("Data: x₁ = (1, 2), y₁ = −1; x₂ = (2, 1), y₂ = +1; x₃ = (−1, −1), y₃ = −1; x₄ = (1, −1), y₄ = +1."),
           tbl([["Sampel", "x", "y", "z = w<super>T</super>x + b", "ŷ", "Δ = η(y − ŷ)", "w sesudah", "b sesudah"],
                ["1", "(1, 2)", "−1", "0", "+1 (z ≥ 0)", "0,1(−1 − 1) = −0,2", "(−0,2; −0,4)", "−0,2"],
                ["2", "(2, 1)", "+1", "−0,4 − 0,4 − 0,2 = −1,0", "−1", "0,1(1 + 1) = +0,2", "(0,2; −0,2)", "0"]],
               [1.3 * cm, 1.4 * cm, 1.0 * cm, 3.6 * cm, 1.9 * cm, 3.1 * cm, 2.6 * cm, 2.1 * cm]),
           P("Perceptron: bobot akhir (0,2; −0,2), bias akhir 0.", "cap"),
           P("<b>ADALINE (batch, n = 4).</b> Iterasi 1: z = 0, e = (−1, 1, −1, 1), J = 0,5; Xᵀe = (3, −1); Xᵀe/n = (0,75; −0,25); mean(e) = 0 → w = (0,075; −0,025), b = 0; J sesudah = 0,441094. "
             "Iterasi 2: z = (0,025; 0,125; −0,05; 0,1), e = (−1,025; 0,875; −0,95; 0,9); Xᵀe = (2,575; −1,125); Xᵀe/n = (0,64375; −0,28125); mean(e) = −0,05 → "
             "<b>w = (0,139375; −0,053125), b = −0,005</b>; J sesudah = 0,393806."),
           P("Lampiran B. Perhitungan manual pada dua sampel data mobil nyata (one-hot mentah, η = 0,1, w = 0, b = 0)", "h1"),
           tbl([["", "buying", "maint", "doors", "persons", "lug_boot", "safety", "y"],
                ["Sampel 1", "high", "vhigh", "5more", "2", "big", "low", "−1"],
                ["Sampel 2", "high", "med", "3", "more", "big", "med", "+1"]], [2.4 * cm, 2.0 * cm, 2.0 * cm, 2.0 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 1.4 * cm]),
           Spacer(1, 3),
           P("Kolom aktif yang dibagi kedua sampel: buying=high dan lug_boot=big. <b>Perceptron.</b> Sampel 1: z = 0 → ŷ = +1, salah; Δ = −0,2, sehingga 6 kolom aktif = −0,2 dan b = −0,2. "
             "Sampel 2: z = (−0,2) + (−0,2) − 0,2 = −0,6 → ŷ = −1, salah; Δ = +0,2, sehingga 6 kolom aktif sampel 2 naik 0,2 dan b = 0. "
             "Bobot akhir: buying=high = lug_boot=big = 0; maint=vhigh = doors=5more = persons=2 = safety=low = −0,2; maint=med = doors=3 = persons=more = safety=med = +0,2; b = 0."),
           P("<b>ADALINE (n = 2).</b> Iterasi 1: z = 0, e = (−1, +1), J = 0,5; Xᵀe/n = (x₂ − x₁)/2, sehingga kolom khusus sampel 2 = +0,5, khusus sampel 1 = −0,5, kolom bersama = 0, mean(e) = 0. "
             "Dengan η = 0,1: ±0,05, b = 0; z = (−0,2; +0,2), e = (−0,8; +0,8), J = 0,32. Iterasi 2: kolom khusus = ±(0,05 + 0,1·0,4) = ±0,09, kolom bersama tetap 0, b = 0; z = (−0,36; +0,36), e = (−0,64; +0,64), J = 0,2048."),
           PageBreak(), P("Lampiran C. Bobot dan bias akhir (21 bobot + bias)", "h1")]
    cols = ["Perceptron η=0.01 std", "ADALINE η=0.1 std", "Perceptron η=0.01 raw", "ADALINE η=0.01 raw"]
    rows = [["Fitur"] + [c.replace("η=", "η = ").replace(" std", " std.").replace(" raw", " tanpa std.") for c in cols]]
    for idx in bw.index: rows.append([idx] + [f2(bw.loc[idx, c], 4) for c in cols])
    st += [tbl(rows, [3.4 * cm, 3.4 * cm, 3.4 * cm, 3.4 * cm, 3.4 * cm]),
           P("Bobot memakai ruang fitur sesuai konfigurasi (terstandardisasi atau mentah). Bobot one-hot tidak unik (Bagian 7e); bandingkan nilainya dalam satu grup atribut.", "cap")]
    out, i = [], 0                      # tabel + keterangannya dijaga satu halaman
    while i < len(st):
        if isinstance(st[i], Table) and i + 1 < len(st) and isinstance(st[i + 1], Paragraph) and st[i + 1].style.name == "c":
            out.append(KeepTogether([st[i], st[i + 1]])); i += 2
        else:
            out.append(st[i]); i += 1
    return out

# ----------------------------------------------------------------------------------- slide
def slides(path):
    W, H = 960, 540
    c = canvas.Canvas(path, pagesize=(W, H)); n = [0]
    ts = lambda size, **k: ParagraphStyle("s", fontName=k.pop("fn", "DV"), fontSize=size, leading=size * 1.32, **k)

    def par(text, x, ytop, w, size=15, **k):
        p = Paragraph(text, ts(size, **k)); _, h = p.wrapOn(c, w, 999); p.drawOn(c, x, ytop - h); return ytop - h

    def img(p, x, ytop, w):
        iw, ih = PILImage.open(p).size; h = w * ih / iw; c.drawImage(p, x, ytop - h, w, h); return ytop - h

    def page(title, sub=None):
        n[0] += 1
        c.setFillColor(colors.white); c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(NAVY); c.rect(0, H - 70, W, 70, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont("DV-B", 25); c.drawString(40, H - 46, title)
        if sub: c.setFont("DV", 12); c.drawRightString(W - 40, H - 44, sub)
        c.setFillColor(colors.HexColor("#777777")); c.setFont("DV", 9)
        c.drawString(40, 18, f"TB1 Jaringan Syaraf Tiruan (IT6053) · Kelompok {GROUP}"); c.drawRightString(W - 40, 18, f"{n[0]} / 7")

    # 1 judul
    page("Perceptron vs ADALINE: kelayakan mobil", "Tugas Besar 1")
    y = par("Klasifikasi dua kelas pada <b>Car Evaluation</b> (UCI), kelanjutan Tugas 1", 50, H - 110, 860, 20, textColor=NAVY)
    y = par("<b>unacc</b> (−1, tidak layak) vs <b>acc</b> (+1, layak, kelas positif) · 1.594 observasi · 6 fitur kategorikal → 21 kolom one-hot", 50, y - 16, 860, 15)
    y = par("<b>Pertanyaan utama:</b> apakah data terpisah linear, dan bagaimana error Perceptron dan ADALINE membuat proses belajarnya berbeda?", 50, y - 24, 860, 16, textColor=TEAL)
    par("<br/>".join(f"{nm} ({nim})" for nm, nim in ANGGOTA), 50, 200, 860, 15, textColor=colors.HexColor("#333333"))
    c.showPage()

    # 2 data
    page("Kasus dan data", "dari Tugas 1 ke TB1")
    par("• <b>Masalah:</b> mobil layak dibeli atau tidak, dari harga beli, perawatan, pintu, penumpang, bagasi, keselamatan.<br/>"
        "• <b>Label</b> dari model pakar DEX, bukan survei pembeli. Data deterministik: semua 1.728 kombinasi atribut.<br/>"
        "• <b>Dua kelas:</b> unacc 1.210 (75,9%) dan acc 384 (24,1%); good/vgood (69/65) dibuang karena terlalu sedikit.<br/>"
        "• Baseline “selalu unacc” = <b>0,7586</b> → wajib lihat precision, recall, F1 kelas positif; FP = kesalahan berbahaya.<br/>"
        "• <b>Split</b> 80:20 berstrata, seed 42: latih 1.275, uji 319. Standardisasi dari data latih saja.<br/>"
        "• Berubah dari Tugas 1: MLP softmax 4 kelas → neuron tunggal 2 kelas; split 70/15/15 → 80:20.", 50, H - 100, 860, 17)
    c.showPage()

    # 3 model
    page("Neuron dan aturan belajar", "z = wᵀx + b;  ŷ = +1 jika z ≥ 0")
    par("<b>Perceptron</b> (per sampel)<br/>error diskret y − ŷ ∈ {0, ±2}<br/>Δ = η(y − ŷ)<br/>w ← w + Δx;  b ← b + Δ<br/>berubah hanya bila salah; tanpa fungsi objektif", 50, H - 100, 420, 17, textColor=NAVY)
    par("<b>ADALINE</b> (batch, Delta Rule)<br/>error kontinu e = y − z<br/>w ← w + η·Xᵀe/n;  b ← b + η·mean(e)<br/>J = (1/2n)Σ(y − z)²; ambang hanya saat prediksi", 500, H - 100, 420, 17, textColor=TEAL)
    par("<b>Verifikasi manual:</b> 2 langkah Perceptron dan 2 iterasi batch ADALINE dihitung tangan (data mini dan data mobil nyata), lalu dicek dengan <code>assert</code> terhadap kode.<br/>"
        "Perceptron: w = (0,2; −0,2), b = 0. ADALINE: w = (0,139375; −0,053125), b = −0,005.<br/>"
        "Inisialisasi nol, urutan data tetap, 50 epoch.", 50, 250, 860, 16)
    c.showPage()

    # 4 eksperimen
    page("Rancangan eksperimen", "8 pelatihan, split dan seed dikunci")
    par("• Perceptron dan ADALINE × η ∈ {0,001; 0,01; 0,1}, 50 epoch, data <b>terstandardisasi</b> (6 pelatihan).<br/>"
        "• + 1 pelatihan <b>tanpa standardisasi</b> per model (η = 0,01) → total 8.<br/>"
        "• Kondisi epoch 10, 30, 50; kurva pembaruan salah (Perceptron) dan J (ADALINE).<br/>"
        "• Data uji hanya untuk pelaporan; <b>tidak ada seleksi memakai data uji</b>; tidak ada kebocoran standardisasi.<br/>"
        "• Diagnostik data latih: Perceptron 2.000 epoch, uji <b>linear programming</b>, ADALINE 3.000 epoch, J* kuadrat terkecil, batas η &lt; 2/λmax.<br/>"
        "• Repository publik: notebook, laporan, dataset, README, requirements; seed 42, Python 3.12.3.", 50, H - 100, 860, 17)
    c.showPage()

    # 5 hasil
    page("Hasil utama", "data uji, 319 sampel")
    rows = [["Konfigurasi", "Akurasi uji", "Precision", "Recall", "F1", "FP"]]
    pick = {"Perceptron η=0.01 std": "Perceptron (η apa pun, std.)", "ADALINE η=0.001 std": "ADALINE η = 0,001", "ADALINE η=0.01 std": "ADALINE η = 0,01",
            "ADALINE η=0.1 std": "ADALINE η = 0,1", "Perceptron η=0.01 raw": "Perceptron η = 0,01 tanpa std.", "ADALINE η=0.01 raw": "ADALINE η = 0,01 tanpa std."}
    for _, r in mk.iterrows():
        if r.Konfigurasi in pick:
            acc = hk[(hk.Model == r.Konfigurasi.split()[0]) & (hk["η"] == float(r.Konfigurasi.split()[1][2:])) & (hk.Standardisasi == ("Ya" if r.Konfigurasi.endswith("std") else "Tidak"))]["Akurasi uji"].iloc[0]
            rows.append([pick[r.Konfigurasi], f2(acc), f2(r["Precision (+1)"], 3), f2(r["Recall (+1)"], 3), f2(r["F1 (+1)"], 3), int(r.FP)])
    data = [[Paragraph(str(x), ts(13, textColor=colors.white if i == 0 else colors.black, fn="DV-B" if i == 0 else "DV")) for x in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[300, 110, 110, 110, 110, 70])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), .5, GRID), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#DDF0EA"))]))
    tw, th = t.wrapOn(c, W, H); t.drawOn(c, 50, H - 100 - th)
    par("Tiga η pada Perceptron menghasilkan <b>hasil identik</b> (η hanya menskalakan bobot). ADALINE η = 0,1 terbaik pada data uji, tetapi ini laporan konfigurasi yang sudah ditetapkan, bukan seleksi. "
        "ADALINE tanpa standardisasi = baseline pada 50 epoch (tidak pernah memprediksi acc).", 50, H - 130 - th, 860, 15)
    c.showPage()

    # 6 pembahasan
    page("Pembahasan", "bukti, bukan hanya akurasi")
    par("• <b>Tidak terpisah linear:</b> LP infeasible; Perceptron tidak pernah 0 pembaruan (min 89, epoch 2.000: 97).<br/>"
        "• <b>Error berbeda:</b> Perceptron dari error diskret, hanya saat salah; ADALINE dari error linear pada semua sampel → J turun mulus ke J* = 0,1938 (η = 0,1).<br/>"
        "• <b>η:</b> tidak berpengaruh pada Perceptron (skala bobot ×10, ×100); sangat berpengaruh pada ADALINE.<br/>"
        "• <b>Standardisasi:</b> mempercepat (κ 13,3 → 1,67). Tanpa standardisasi, ADALINE baru mencapai J* setelah ±1.000 epoch.<br/>"
        "• <b>Akurasi sama ≠ belajar sama:</b> profil FP/FN berbeda (FP 28 vs 10).", 40, H - 95, 880, 14.5)
    img("figures/kurva_adaline.png", 70, 260, 820)
    c.showPage()

    # 7 kesimpulan
    page("Kesimpulan dan keterbatasan", "demo: jalankan notebook")
    par("• Kedua model diimplementasikan mandiri dengan NumPy; hitungan manual cocok dengan kode.<br/>"
        "• Data latih tidak terpisah linear; model linear pada one-hot tidak menangkap interaksi atribut aturan pakar.<br/>"
        "• ADALINE konvergen ke solusi kuadrat terkecil dan memberi FP lebih sedikit; Perceptron berfluktuasi tanpa konvergensi.<br/>"
        "• <b>Keterbatasan:</b> satu split dan seed, 319 sampel uji, data deterministik (bukan populasi nyata), hanya 2 dari 4 kelas, one-hot kolinear.<br/>"
        "• <b>Berikutnya:</b> fitur interaksi atau MLP, validasi silang, penyesuaian ambang untuk menekan FP, one-vs-rest 4 kelas.", 50, H - 100, 860, 17)
    par("Setiap anggota siap menjelaskan data, aturan pembaruan, hasil, dan kontribusinya; notebook siap dijalankan.", 50, 120, 860, 15, textColor=TEAL)
    c.showPage(); c.save()

if __name__ == "__main__":
    out_r = f"TB1_Kelompok{GROUP}.pdf"
    doc = SimpleDocTemplate(out_r, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title=f"TB1 Kelompok {GROUP}: Perceptron dan ADALINE", author="Kelompok " + GROUP)
    doc.build(laporan(), onFirstPage=cover, onLaterPages=footer)
    slides("Presentasi_TB1.pdf")
    print("OK:", out_r, "dan Presentasi_TB1.pdf")
