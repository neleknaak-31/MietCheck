"""
MietCheck – zentrale Konfiguration
==================================
Ein Ort für alle Pfade, Spaltennamen und fachlichen Grenzwerte.
So bleiben Datenaufbereitung (data_prep.py), Training (train.py) und
App (app.py) garantiert konsistent.
"""
from pathlib import Path

# --- Projektpfade -----------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"

RAW_CSV = DATA_DIR / "immo_data.csv"          # Rohdaten von Kaggle (Immoscout24)
CLEAN_PARQUET = DATA_DIR / "immo_clean.parquet"  # Ergebnis der Datenphase
MODEL_FILE = MODEL_DIR / "mietcheck_model.joblib"
META_FILE = MODEL_DIR / "meta.json"           # Dropdown-Optionen + Kennzahlen für die App

for d in (DATA_DIR, MODEL_DIR, REPORT_DIR):
    d.mkdir(exist_ok=True)

# --- Zielgröße --------------------------------------------------------------
# Wir sagen die KALTMIETE (baseRent) voraus – der Standardwert für einen
# Mietspiegel-Vergleich und im Datensatz zu 100 % befuellt.
TARGET = "baseRent"

# --- Merkmale, die der Nutzer kennt (bewusst schlank fuer eine einfache UX) --
NUMERIC_FEATURES = ["livingSpace", "noRooms", "yearConstructed"]
CATEGORICAL_FEATURES = ["regio1", "regio2", "condition", "interiorQual", "typeOfFlat"]
BOOLEAN_FEATURES = ["balcony", "hasKitchen", "cellar", "lift", "garden", "newlyConst"]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES + BOOLEAN_FEATURES

# --- Fachliche Plausibilitaetsgrenzen (Qualitaetspruefung) ------------------
# Angebote ausserhalb dieser Grenzen sind Tipp-/Datenfehler und werden entfernt.
LIMITS = {
    "baseRent":        (100, 6000),    # EUR Kaltmiete
    "livingSpace":     (15, 300),      # m2
    "noRooms":         (1, 8),         # Zimmer
    "yearConstructed": (1900, 2025),   # Baujahr
    "eur_per_sqm":     (3, 40),        # EUR/m2 – faengt harte Ausreisser ab
}

# Klartext-Labels fuer die App (Rohwerte -> verstaendliches Deutsch)
CONDITION_LABELS = {
    "first_time_use": "Erstbezug",
    "first_time_use_after_refurbishment": "Erstbezug nach Sanierung",
    "mint_condition": "Neuwertig",
    "fully_renovated": "Komplett renoviert",
    "refurbished": "Saniert",
    "modernized": "Modernisiert",
    "well_kept": "Gepflegt",
    "negotiable": "Nach Vereinbarung",
    "need_of_renovation": "Renovierungsbeduerftig",
    "ripe_for_demolition": "Abrissreif",
}
QUALITY_LABELS = {
    "simple": "Einfach",
    "normal": "Normal",
    "sophisticated": "Gehoben",
    "luxury": "Luxus",
}
FLAT_LABELS = {
    "apartment": "Etagenwohnung",
    "ground_floor": "Erdgeschoss",
    "raised_ground_floor": "Hochparterre",
    "roof_storey": "Dachgeschoss",
    "half_basement": "Souterrain",
    "terraced_flat": "Terrassenwohnung",
    "maisonette": "Maisonette",
    "penthouse": "Penthouse",
    "loft": "Loft",
    "other": "Sonstige",
}

BUNDESLAND_LABELS = {
    "Baden_Württemberg": "Baden-Württemberg",
    "Nordrhein_Westfalen": "Nordrhein-Westfalen",
    "Rheinland_Pfalz": "Rheinland-Pfalz",
    "Sachsen_Anhalt": "Sachsen-Anhalt",
    "Schleswig_Holstein": "Schleswig-Holstein",
    "Mecklenburg_Vorpommern": "Mecklenburg-Vorpommern",
}

# Schwellen fuer das Urteil (Abweichung Angebot vs. faire Miete)
VERDICT_BANDS = {
    "bargain":   -0.10,   # <= -10 %  -> Schnaeppchen
    "fair_low":  -0.10,
    "fair_high":  0.10,   # zwischen -10 % und +10 % -> fair
    "expensive":  0.10,   # > +10 %   -> zu teuer
}

RANDOM_STATE = 42
