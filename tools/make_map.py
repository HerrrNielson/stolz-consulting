# -*- coding: utf-8 -*-
"""Erzeugt mapdata.py (vereinfachte Weltkarte als SVG-Pfade) aus Natural Earth.

Quelle: Natural Earth, ne_110m_admin_0_countries (Public Domain, https://www.naturalearthdata.com/)
Aufruf: python tools/make_map.py pfad/zu/ne_110m_admin_0_countries.geojson
Projektion: Miller (zylindrisch), Ausschnitt 56 S bis 80 N, Breite 1000, Genauigkeit 1 Nachkommastelle.
Die Marker-Koordinaten in build.py (MAP_PLACES) nutzen Längen-/Breitengrad und werden mit project() umgerechnet.
"""
import json, math, sys
from pathlib import Path

W = 1000.0
LAT_MIN, LAT_MAX = -56.0, 80.0
HIGHLIGHT = {"RU", "CN", "US", "FR", "DE", "AT", "EE", "LV", "LT"}
ISO_FIX = {"France": "FR", "Norway": "NO"}  # Natural Earth hat ISO_A2 = -99 für diese


def mill(lat):
    return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))


Y0, Y1 = mill(LAT_MAX), mill(LAT_MIN)
K = W / (2 * math.pi)
H = round((Y0 - Y1) * K, 1)


def project(lon, lat):
    return round((lon + 180) / 360 * W, 1), round((Y0 - mill(lat)) * K, 1)


def dp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1e-9
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / n
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return dp(pts[:idx + 1], eps)[:-1] + dp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def ring_path(ring):
    pts = [project(lo, la) for lo, la in ring]
    if all(p[1] < -5 for p in pts):
        return ""
    h = len(pts) // 2
    pts = dp(pts[:h + 1], 0.8)[:-1] + dp(pts[h:], 0.8)
    if len(pts) < 4:
        return ""
    # Fläche prüfen: Kleinstflächen weglassen
    a = abs(sum(pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1] for i in range(len(pts) - 1))) / 2
    if a < 8:
        return ""
    s = "M" + " ".join(f"{x:g},{y:g}" for x, y in pts[:-1]) + "Z"
    return s


def main(src):
    gj = json.loads(Path(src).read_text(encoding="utf-8"))
    land, hi = [], {}
    for f in gj["features"]:
        p = f["properties"]
        iso = p.get("ISO_A2") if p.get("ISO_A2") not in (None, "-99") else p.get("ISO_A2_EH")
        iso = ISO_FIX.get(p.get("NAME"), iso)
        if p.get("NAME") == "Antarctica":
            continue
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        if iso == "FR":  # Französisch-Guayana u. a. Überseegebiete nicht mitfärben (Belegt ist Frankreich/Europa)
            polys = [q for q in polys if q[0][0][1] > 35]
        d = "".join(ring_path(poly[0]) for poly in polys)
        if not d:
            continue
        if iso in HIGHLIGHT:
            hi[iso] = d
        else:
            land.append(d)
    out = ['# -*- coding: utf-8 -*-',
           '"""AUTOMATISCH ERZEUGT von tools/make_map.py - nicht von Hand bearbeiten.',
           'Geometrie: Natural Earth 110m (Public Domain), vereinfacht, Miller-Projektion."""',
           f"MAP_W = {int(W)}", f"MAP_H = {H:g}",
           f"MAP_LAND = {''.join(land)!r}",
           f"MAP_COUNTRIES = {hi!r}", ""]
    Path(__file__).resolve().parent.parent.joinpath("mapdata.py").write_text("\n".join(out), encoding="utf-8")
    print("land", sum(map(len, land)), "hi", {k: len(v) for k, v in hi.items()}, "H", H)


if __name__ == "__main__":
    main(sys.argv[1])
