"""Rekonstruksi car.data (UCI Car Evaluation) dari tabel aturan model keputusan DEX yang dipublikasikan
(Bohanec & Rajkovic; halaman dataset https://file.biolab.si/biolab/app/hint/car_dataset.html).
Data UCI mencakup SEMUA kombinasi atribut (4*4*4*3*3*3 = 1728) dan label adalah fungsi deterministik dari
tabel-tabel tersebut. Hasil diverifikasi dengan distribusi kelas resmi: unacc 1210, acc 384, good 69, vgood 65.
Jika ingin memakai berkas asli, unduh car.data dari UCI (dataset 19) -- isinya harus identik."""
import itertools, csv
BUY = ["vhigh", "high", "med", "low"]; DOORS = ["2", "3", "4", "5more"]
PERS = ["2", "4", "more"]; LUG = ["small", "med", "big"]; SAFE = ["low", "med", "high"]
# PRICE(buying, maint)
_p = {  # kunci: maint -> urutan buying [vhigh, high, med, low]
 "vhigh": ["vhigh", "vhigh", "high", "high"], "high": ["vhigh", "high", "high", "med"],
 "med":   ["high", "high", "med", "low"],     "low":  ["high", "high", "low", "low"]}
price = lambda b, m: _p[m][BUY.index(b)]
# COMFORT(doors, persons, lug_boot)
def comfort(d, p, l):
    if p == "2": return "bad"
    di = DOORS.index(d)
    if p == "4":
        return {"small": ["acc"]*4, "med": ["acc", "acc", "good", "vgood"], "big": ["good", "good", "vgood", "vgood"]}[l][di]
    return {"small": ["bad", "acc", "acc", "acc"], "med": ["acc", "good", "vgood", "vgood"], "big": ["good", "vgood", "vgood", "vgood"]}[l][di]
# TECH(COMFORT, safety)
_t = {"low": {"bad": "poor", "acc": "poor", "good": "poor", "vgood": "poor"},
      "med": {"bad": "poor", "acc": "satisf", "good": "good", "vgood": "good"},
      "high": {"bad": "poor", "acc": "good", "good": "vgood", "vgood": "vgood"}}
tech = lambda c, s: _t[s][c]
# CAR(PRICE, TECH)
_c = {"poor": dict(vhigh="unacc", high="unacc", med="unacc", low="unacc"),
      "satisf": dict(vhigh="unacc", high="unacc", med="acc", low="acc"),
      "good": dict(vhigh="unacc", high="acc", med="acc", low="good"),
      "vgood": dict(vhigh="unacc", high="acc", med="vgood", low="vgood")}
car = lambda p, t: _c[t][p]

rows = []
for b, m, d, p, l, s in itertools.product(BUY, BUY, DOORS, PERS, LUG, SAFE):   # urutan sama dengan car.data
    rows.append([b, m, d, p, l, s, car(price(b, m), tech(comfort(d, p, l), s))])
if __name__ == "__main__":
    from collections import Counter
    cnt = Counter(r[-1] for r in rows); print(len(rows), dict(cnt))
    assert len(rows) == 1728 and cnt == {"unacc": 1210, "acc": 384, "good": 69, "vgood": 65}
    with open("car_evaluation_full.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["buying", "maint", "doors", "persons", "lug_boot", "safety", "class"]); w.writerows(rows)
    print("OK: distribusi cocok dengan data resmi UCI; baris pertama:", rows[0], "terakhir:", rows[-1])
