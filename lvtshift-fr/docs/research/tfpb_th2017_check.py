"""Independent check of today's TFPB split, from the 2017 taxe d'habitation.

In 2017 the taxe d'habitation (TH) still fell on every occupied dwelling, on
the same 1970 rental values as the TFPB, whose base is half the rental value
(CGI art. 1388). So, per commune,

    housing share of the TFPB base  ~  0.5 x J11 / E11      (REI 2017)

with J11 the gross TH rental value of the commune's premises and E11 its net
TFPB base. The rest is business premises plus industrial establishments, at
2017 values (before industrial values were halved in 2021).

Usage:
    python tfpb_th2017_check.py REI-2017-fichier-notice-trace.zip [INSEE ...]

The zip is the DGFiP REI 2017 file (data.gouv.fr dataset « Impôts locaux :
fichier de recensement des éléments d'imposition à la fiscalité directe
locale (REI) »). Prints the national ratios and one line per INSEE code.
Reads python-calamine when installed (≈ 10 s), else openpyxl (several
minutes). See tfpb-baseline-calibration.md §9.5.
"""

import sys
import zipfile
from pathlib import Path

COLS = ["DEP", "COM", "LIBCOM", "E11", "J11", "T29"]
MEMBER = "REI-2017-fichier-notice-trace/REI_COMPLET_2017.xlsx"


def read_rows(zip_path: str):
    out_dir = Path(zip_path).parent          # extracts next to the zip, once
    xlsx = out_dir / MEMBER
    if not xlsx.exists():
        zipfile.ZipFile(zip_path).extract(MEMBER, out_dir)
    try:
        from python_calamine import CalamineWorkbook
        data = CalamineWorkbook.from_path(str(xlsx)).get_sheet_by_index(0).to_python()
        hdr, rows = [str(h) for h in data[0]], data[1:]
    except ImportError:
        import openpyxl
        ws = openpyxl.load_workbook(xlsx, read_only=True).worksheets[0]
        it = ws.iter_rows(values_only=True)
        hdr, rows = [str(h) for h in next(it)], it
    idx = [hdr.index(c) for c in COLS]
    for r in rows:
        yield dict(zip(COLS, (r[i] for i in idx)))


def num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def main(zip_path: str, codes: list) -> None:
    tot = {"E11": 0.0, "J11": 0.0, "T29": 0.0}
    found = {}
    for r in read_rows(zip_path):
        for k in tot:
            tot[k] += num(r[k])
        code = str(r["DEP"]).zfill(2)[:2] + str(r["COM"]).split(".")[0].zfill(3)
        if code in codes:
            found[code] = r
    h = 0.5 * tot["J11"] / tot["E11"]
    print(f"France 2017: E11 {tot['E11'] / 1e9:.1f} bn, J11 {tot['J11'] / 1e9:.1f} bn; "
          f"housing {h:.3f}, non-housing {1 - h:.3f}, CFE proxy {0.5 * tot['T29'] / tot['E11']:.3f}")
    for code in codes:
        r = found.get(code)
        if r is None:
            print(f"{code}: not in REI 2017")
            continue
        e11, j11 = num(r["E11"]), num(r["J11"])
        h = 0.5 * j11 / e11 if e11 else float("nan")
        print(f"{code} {r['LIBCOM']}: housing {h:.3f}, non-housing {1 - h:.3f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
