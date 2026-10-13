"""Verifikasi car_evaluation_full.csv terhadap car.data ASLI dari UCI (dataset 19).

Cara pakai (dari direktori utama repo):
    1. Unduh car.data dari https://archive.ics.uci.edu/dataset/19/car+evaluation
       (berkas tanpa header; 1728 baris: buying,maint,doors,persons,lug_boot,safety,class).
    2. python scripts/verifikasi_car_data.py path/ke/car.data

Keluaran: IDENTIK (isi dan urutan sama) atau daftar perbedaan. Catat hasilnya di README.
Jika berbeda, ganti car_evaluation_full.csv dan dataset.csv dengan data asli, lalu jalankan ulang notebook.
"""
import csv, sys

def baca(path, header):
    with open(path, newline="") as f:
        rows = [tuple(c.strip() for c in r) for r in csv.reader(f) if r]
    return rows[1:] if header else rows

def main(path_asli):
    asli = baca(path_asli, header=False)
    kami = baca("car_evaluation_full.csv", header=True)
    print(f"Baris car.data asli: {len(asli)} | car_evaluation_full.csv: {len(kami)}")
    sama_set, sama_urut = set(asli) == set(kami), asli == kami
    if sama_urut:
        print("HASIL: IDENTIK (isi dan urutan baris sama persis).")
    elif sama_set and len(asli) == len(kami):
        print("HASIL: ISI SAMA, tetapi urutan baris berbeda. Urutan memengaruhi hasil split (random_state), jadi ganti berkas dengan data asli dan jalankan ulang notebook.")
    else:
        sel_a, sel_k = set(asli) - set(kami), set(kami) - set(asli)
        print(f"HASIL: BERBEDA. Hanya di car.data asli: {len(sel_a)} baris; hanya di berkas ini: {len(sel_k)} baris.")
        for r in sorted(sel_a)[:10]: print("  asli  :", ",".join(r))
        for r in sorted(sel_k)[:10]: print("  berkas:", ",".join(r))
    # dataset.csv harus himpunan bagian (unacc + acc) dari data yang diverifikasi
    ds = baca("dataset.csv", header=True)
    pakai = {r for r in asli if r[-1] in ("unacc", "acc")}
    print("dataset.csv sama dengan baris unacc+acc di car.data asli:", set(ds) == pakai and len(ds) == len(pakai))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
