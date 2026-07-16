"""
MietCheck – QUA3CK-Phase Q + U : Qualitaetspruefung & Understanding the Data
============================================================================
Schritte:
  1. Rohdaten laden (Immoscout24 / Kaggle)
  2. Qualitaetspruefung: unplausible Werte & Ausreisser entfernen
  3. Understanding the Data: EDA-Grafiken erzeugen (seaborn)
  4. Merkmale auswaehlen, sauberen Datensatz + Metadaten speichern

Aufruf:  python3 src/data_prep.py
"""
import json
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import (BOOLEAN_FEATURES, CATEGORICAL_FEATURES, CLEAN_PARQUET,
                    FEATURES, LIMITS, META_FILE, NUMERIC_FEATURES, RAW_CSV,
                    REPORT_DIR, TARGET)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="rocket")


def load_raw() -> pd.DataFrame:
    print(f"→ Lade Rohdaten: {RAW_CSV.name}")
    df = pd.read_csv(RAW_CSV, low_memory=False)
    print(f"  Rohdaten: {df.shape[0]:,} Zeilen × {df.shape[1]} Spalten")
    return df


def quality_check(df: pd.DataFrame) -> pd.DataFrame:
    """QUA3CK-Q: harte Datenqualitaet herstellen."""
    n0 = len(df)
    keep = [c for c in FEATURES + [TARGET] if c in df.columns]
    df = df[keep].copy()

    # Zielgroesse muss vorhanden sein
    df = df.dropna(subset=[TARGET, "livingSpace", "noRooms"])

    # Plausibilitaetsgrenzen anwenden
    for col, (lo, hi) in LIMITS.items():
        if col == "eur_per_sqm":
            continue
        if col in df.columns:
            df = df[(df[col] >= lo) & (df[col] <= hi)]

    # EUR/m2 – faengt Datenfehler ab (z.B. 5 EUR Kaltmiete oder 9.999.999 EUR)
    lo, hi = LIMITS["eur_per_sqm"]
    eur_sqm = df[TARGET] / df["livingSpace"]
    df = df[(eur_sqm >= lo) & (eur_sqm <= hi)]

    print(f"→ Qualitaetspruefung: {n0:,} → {len(df):,} Zeilen "
          f"({(1 - len(df)/n0) * 100:.1f} % entfernt)")
    return df.reset_index(drop=True)


def eda(df: pd.DataFrame) -> None:
    """QUA3CK-U: Understanding the Data – zentrale Grafiken speichern."""
    print("→ Erzeuge EDA-Grafiken …")

    # 1) Verteilung der Kaltmiete
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(df[TARGET], bins=60, ax=ax[0], color="#b5179e")
    ax[0].set(title="Verteilung Kaltmiete (EUR)", xlabel="Kaltmiete")
    sns.histplot(np.log1p(df[TARGET]), bins=60, ax=ax[1], color="#7209b7")
    ax[1].set(title="Kaltmiete – log-transformiert", xlabel="log(1+Kaltmiete)")
    fig.tight_layout(); fig.savefig(REPORT_DIR / "01_zielverteilung.png", dpi=110); plt.close(fig)

    # 2) Preis pro m2 je Bundesland (der Kern des USP)
    df = df.assign(eur_sqm=df[TARGET] / df["livingSpace"])
    order = df.groupby("regio1")["eur_sqm"].median().sort_values(ascending=False).index
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.boxplot(data=df, x="regio1", y="eur_sqm", order=order, ax=ax, showfliers=False)
    ax.set(title="Kaltmiete pro m² nach Bundesland", xlabel="", ylabel="EUR / m²")
    ax.tick_params(axis="x", rotation=60)
    fig.tight_layout(); fig.savefig(REPORT_DIR / "02_preis_pro_qm_bundesland.png", dpi=110); plt.close(fig)

    # 3) Korrelationen der numerischen Merkmale
    num = df[NUMERIC_FEATURES + [TARGET, "eur_sqm"]]
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(num.corr(), annot=True, fmt=".2f", cmap="rocket_r", ax=ax)
    ax.set(title="Korrelationsmatrix")
    fig.tight_layout(); fig.savefig(REPORT_DIR / "03_korrelation.png", dpi=110); plt.close(fig)

    # 4) Wohnflaeche vs. Miete
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df.sample(min(8000, len(df)), random_state=1),
                    x="livingSpace", y=TARGET, hue="noRooms",
                    alpha=0.4, palette="rocket", ax=ax)
    ax.set(title="Wohnfläche vs. Kaltmiete", xlabel="Wohnfläche (m²)", ylabel="Kaltmiete (EUR)")
    fig.tight_layout(); fig.savefig(REPORT_DIR / "04_flaeche_vs_miete.png", dpi=110); plt.close(fig)

    print(f"  4 Grafiken gespeichert in {REPORT_DIR}/")


def build_meta(df: pd.DataFrame) -> None:
    """Dropdown-Optionen & Kennzahlen fuer die App ableiten."""
    # Staedte je Bundesland (nach Haeufigkeit sortiert, min. 30 Angebote)
    cities = {}
    for bl in sorted(df["regio1"].unique()):
        vc = df.loc[df["regio1"] == bl, "regio2"].value_counts()
        cities[bl] = vc[vc >= 30].index.tolist()

    meta = {
        "n_clean": int(len(df)),
        "bundeslaender": sorted(df["regio1"].unique().tolist()),
        "cities_by_bl": cities,
        "conditions": df["condition"].dropna().value_counts().index.tolist(),
        "qualities": df["interiorQual"].dropna().value_counts().index.tolist(),
        "flat_types": df["typeOfFlat"].dropna().value_counts().index.tolist(),
        "defaults": {
            "condition": df["condition"].mode(dropna=True).iloc[0],
            "interiorQual": df["interiorQual"].mode(dropna=True).iloc[0],
            "typeOfFlat": df["typeOfFlat"].mode(dropna=True).iloc[0],
            "yearConstructed": int(df["yearConstructed"].median()),
        },
    }
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"→ Metadaten gespeichert: {META_FILE.name} "
          f"({len(meta['bundeslaender'])} Bundeslaender)")


def main():
    df = load_raw()
    df = quality_check(df)
    eda(df)
    build_meta(df)
    df.to_parquet(CLEAN_PARQUET, index=False)
    print(f"✔ Sauberer Datensatz gespeichert: {CLEAN_PARQUET.name} "
          f"({len(df):,} Zeilen)")


if __name__ == "__main__":
    main()
