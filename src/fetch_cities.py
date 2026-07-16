"""
MietCheck – Städte-Daten aus dem Web (OpenPLZ API)
==================================================
Holt ALLE deutschen Gemeinden über die offene OpenPLZ API
(https://openplzapi.org, kein API-Key nötig) und ordnet jede Stadt ihrem
Landkreis zu – also dem `regio2`, auf dem das Modell trainiert ist.

Ergebnis: data/cities_de.json  (wird mitgeliefert, App läuft damit offline).

Aufruf:  python3 src/fetch_cities.py
"""
import json
import ssl
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

import pandas as pd

from config import CLEAN_PARQUET, DATA_DIR, TARGET

BASE = "https://openplzapi.org/de"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
CITIES_FILE = DATA_DIR / "cities_de.json"


def _get(path):
    """GET mit kleiner Wiederholung; gibt geparste JSON-Liste zurück."""
    url = f"{BASE}/{path}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MietCheck/1.0"})
            with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            time.sleep(0.5 * (attempt + 1))
    return []


def _paged(path):
    """Alle Seiten eines Endpunkts einsammeln (pageSize=50 = API-Maximum)."""
    out, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        batch = _get(f"{path}{sep}page={page}&pageSize=50")
        if not batch:
            break
        out.extend(batch)
        if len(batch) < 50:
            break
        page += 1
    return out


def norm(s: str) -> str:
    """Ortsname -> Trainingsschreibweise (Umlaute bleiben, Rest wird _)."""
    s = s.split(",")[0].strip()                 # ", Landeshauptstadt" etc. abschneiden
    for a in [" ", "-", "/", "."]:
        s = s.replace(a, "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


def match_regio2(dist_name: str, dist_type: str, known: set):
    """Landkreis der API auf ein bekanntes Trainings-regio2 abbilden (oder None)."""
    base = norm(dist_name)
    if dist_type == "Landkreis":
        cands = ([base, base + "_Kreis"] if "kreis" in base.lower()
                 else [base + "_Kreis", base])
    else:  # Kreisfreie Stadt / Stadtkreis / Regionalverband
        cands = [base, base + "_Kreis"]
    for c in cands:
        if c in known:
            return c
    return None


def main():
    print("→ Lade bekannte Regionen aus den Trainingsdaten …")
    df = pd.read_parquet(CLEAN_PARQUET)
    known = set(df["regio2"].dropna().unique())
    train_counts = df.groupby("regio2")[TARGET].size().to_dict()

    print("→ Lade Bundesländer …")
    states = _get("FederalStates")
    print(f"  {len(states)} Bundesländer")

    # 1) alle Landkreise je Bundesland
    print("→ Lade Landkreise je Bundesland …")
    districts = []
    for s in states:
        ds = _paged(f"FederalStates/{s['key']}/Districts")
        for d in ds:
            d["_bl"] = s["name"].replace("-", "_")   # -> Trainings-regio1
        districts.extend(ds)
    print(f"  {len(districts)} Landkreise / kreisfreie Städte")

    # 2) alle Gemeinden je Landkreis (parallel)
    print("→ Lade Gemeinden (parallel) …")

    def fetch_muni(d):
        munis = _paged(f"Districts/{quote(d['key'])}/Municipalities")
        return d, munis

    all_rows, done = [], 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for d, munis in ex.map(fetch_muni, districts):
            r2 = match_regio2(d["name"], d["type"], known)
            for m in munis:
                if "gemeindefrei" in m.get("type", "").lower():
                    continue  # Wälder/Seen ohne Einwohner überspringen
                nm = m["name"].split(",")[0].strip()  # ", St"/", M" etc. entfernen
                all_rows.append({
                    "name": nm, "plz": m.get("postalCode", ""),
                    "bl": d["_bl"], "district": d["name"].split(",")[0].strip(),
                    "regio2": r2,
                })
            done += 1
            if done % 80 == 0:
                print(f"  … {done}/{len(districts)} Landkreise")
    print(f"  {len(all_rows):,} Gemeinden geladen")

    # 3) je Bundesland aufbereiten: dedupen, Duplikate mit Kreis kennzeichnen
    cities_by_bl = {}
    for bl in sorted({r["bl"] for r in all_rows}):
        rows = [r for r in all_rows if r["bl"] == bl]
        name_counts = {}
        for r in rows:
            name_counts[r["name"]] = name_counts.get(r["name"], 0) + 1
        seen, items = set(), []
        for r in sorted(rows, key=lambda x: x["name"]):
            label = (f"{r['name']} ({r['district']})"
                     if name_counts[r["name"]] > 1 else r["name"])
            if label in seen:
                continue
            seen.add(label)
            items.append({"label": label, "regio2": r["regio2"]})
        cities_by_bl[bl] = items

    # Garantie: jede Trainings-Region ist auswählbar (Stadtstaaten wie Berlin/
    # Hamburg listet die API nicht als Gemeinde) – sonst fehlten sie im Dropdown.
    bl_of = df.groupby("regio2")["regio1"].first().to_dict()
    for r2, bl in bl_of.items():
        lst = cities_by_bl.setdefault(bl, [])
        if not any(it["regio2"] == r2 for it in lst):
            label = r2.replace("_Kreis", " (Landkreis)").replace("_", " ")
            lst.append({"label": label, "regio2": r2})
    # Dubletten je Label entfernen; Eintrag mit Landkreis-Treffer bevorzugen
    for bl in cities_by_bl:
        best = {}
        for it in cities_by_bl[bl]:
            cur = best.get(it["label"])
            if cur is None or (not cur["regio2"] and it["regio2"]):
                best[it["label"]] = it
        cities_by_bl[bl] = sorted(best.values(), key=lambda x: x["label"])

    matched = sum(1 for r in all_rows if r["regio2"])
    n_select = sum(len(v) for v in cities_by_bl.values())
    meta = {
        "source": "OpenPLZ API (openplzapi.org)",
        "n_cities": n_select,
        "n_api_cities": len(all_rows),
        "n_matched_regio2": matched,
        "match_rate": round(matched / max(1, len(all_rows)) * 100, 1),
        "n_bundeslaender": len(cities_by_bl),
        "cities_by_bl": cities_by_bl,
        "regio2_counts": train_counts,
    }
    CITIES_FILE.write_text(json.dumps(meta, ensure_ascii=False))
    print(f"\n✔ Gespeichert: {CITIES_FILE.name}")
    print(f"  {len(all_rows):,} Städte · {meta['match_rate']} % einem "
          f"Trainings-Landkreis zugeordnet · {len(cities_by_bl)} Bundesländer")


if __name__ == "__main__":
    main()
