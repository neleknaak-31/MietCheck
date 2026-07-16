"""
MietCheck – QUA3CK-Phase A + Modellentwicklung + C (Kreuzvalidierung)
====================================================================
  A  Algorithmenauswahl : mehrere Modelle vergleichen
     Modellentwicklung  : sklearn-Pipeline (Imputation + Scaling + One-Hot)
  C  Kreuzvalidierung   : 5-fache CV, bestes Modell waehlen & sichern
  K  Wissensextraktion  : Merkmalswichtigkeit als Grafik

Aufruf:  python3 src/train.py
"""
import json
import time
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import (BOOLEAN_FEATURES, CATEGORICAL_FEATURES, CLEAN_PARQUET,
                    FEATURES, MODEL_FILE, NUMERIC_FEATURES, RANDOM_STATE,
                    REPORT_DIR, TARGET)

warnings.filterwarnings("ignore")


def build_preprocessor() -> ColumnTransformer:
    """Datenaufbereitung als wiederverwendbarer Baustein (Datenphase im Modell)."""
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),   # fehlende Baujahre etc.
        ("scale", StandardScaler()),                     # Feature-Scaling
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=30,
                                 sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", numeric, NUMERIC_FEATURES),
        ("cat", categorical, CATEGORICAL_FEATURES),
        ("bool", "passthrough", BOOLEAN_FEATURES),
    ])


def get_models(pre) -> dict:
    """QUA3CK-A: Kandidaten-Algorithmen."""
    return {
        "Lineare Regression": Pipeline([("pre", pre), ("m", LinearRegression())]),
        "Random Forest": Pipeline([("pre", pre), ("m", RandomForestRegressor(
            n_estimators=120, max_depth=22, min_samples_leaf=4,
            n_jobs=-1, random_state=RANDOM_STATE))]),
        "Gradient Boosting": Pipeline([("pre", pre), ("m", HistGradientBoostingRegressor(
            max_iter=400, learning_rate=0.08, max_depth=None,
            l2_regularization=1.0, random_state=RANDOM_STATE))]),
    }


def main():
    print("→ Lade sauberen Datensatz …")
    df = pd.read_parquet(CLEAN_PARQUET)
    X, y = df[FEATURES], df[TARGET]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE)
    print(f"  Training: {len(X_tr):,}  |  Test: {len(X_te):,}")

    pre = build_preprocessor()
    models = get_models(pre)

    # --- QUA3CK-C: Kreuzvalidierung zum fairen Vergleich --------------------
    results, best_name, best_score = {}, None, -np.inf
    for name, pipe in models.items():
        t0 = time.time()
        cv_mae = -cross_val_score(pipe, X_tr, y_tr, cv=5,
                                  scoring="neg_mean_absolute_error", n_jobs=-1)
        results[name] = {"cv_mae": float(cv_mae.mean()), "cv_std": float(cv_mae.std())}
        print(f"  {name:<20} CV-MAE = {cv_mae.mean():6.1f} € "
              f"(±{cv_mae.std():4.1f})   [{time.time()-t0:4.1f}s]")
        if -cv_mae.mean() > best_score:
            best_score, best_name = -cv_mae.mean(), name

    print(f"\n★ Bestes Modell (CV): {best_name}")

    # --- Bestes Modell final trainieren & auf Testset bewerten -------------
    best = models[best_name].fit(X_tr, y_tr)
    pred = best.predict(X_te)
    mae = mean_absolute_error(y_te, pred)
    r2 = r2_score(y_te, pred)
    mape = float(np.mean(np.abs((y_te - pred) / y_te)) * 100)
    print(f"  Test-MAE  = {mae:.1f} €")
    print(f"  Test-R²   = {r2:.3f}")
    print(f"  Test-MAPE = {mape:.1f} %")

    # --- Modell auf ALLEN Daten trainieren fuer die App --------------------
    final = models[best_name].fit(X, y)
    dump(final, MODEL_FILE)
    print(f"✔ Modell gespeichert: {MODEL_FILE.name}")

    # --- Kennzahlen sichern ------------------------------------------------
    metrics = {"best_model": best_name, "test_mae": round(mae, 1),
               "test_r2": round(r2, 3), "test_mape": round(mape, 1),
               "cv_results": results, "n_train": len(X)}
    (REPORT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))

    # --- QUA3CK-K: Merkmalswichtigkeit (Permutation) -----------------------
    plot_importance(final, best_name, X_te, y_te)

    # --- Grafik: Vorhersage vs. Realitaet ----------------------------------
    fig, ax = plt.subplots(figsize=(6, 6))
    idx = np.random.RandomState(0).choice(len(y_te), min(4000, len(y_te)), replace=False)
    ax.scatter(np.asarray(y_te)[idx], pred[idx], alpha=0.25, s=10, color="#b5179e")
    lim = [0, np.percentile(y_te, 99)]
    ax.plot(lim, lim, "--", color="#333")
    ax.set(xlim=lim, ylim=lim, xlabel="Tatsächliche Kaltmiete (€)",
           ylabel="Vorhergesagt (€)", title=f"{best_name}: Vorhersage vs. Realität")
    fig.tight_layout(); fig.savefig(REPORT_DIR / "05_pred_vs_real.png", dpi=110); plt.close(fig)
    print(f"✔ Report-Grafiken gespeichert in {REPORT_DIR}/")


def plot_importance(pipe, name, X_te, y_te):
    """Permutations-Wichtigkeit: modell-agnostisch, direkt je Roh-Merkmal."""
    from sklearn.inspection import permutation_importance
    try:
        n = min(6000, len(X_te))
        Xs, ys = X_te.iloc[:n], y_te.iloc[:n]
        r = permutation_importance(pipe, Xs, ys, n_repeats=5,
                                   random_state=RANDOM_STATE, n_jobs=-1,
                                   scoring="neg_mean_absolute_error")
        imp = pd.Series(r.importances_mean, index=FEATURES).sort_values()
        fig, ax = plt.subplots(figsize=(8, 5))
        imp.plot.barh(ax=ax, color="#7209b7")
        ax.set(title=f"Merkmalswichtigkeit ({name}, Permutation)",
               xlabel="Anstieg des MAE bei Zufalls-Permutation (€)")
        fig.tight_layout(); fig.savefig(REPORT_DIR / "06_merkmalswichtigkeit.png", dpi=110)
        plt.close(fig)
        print(f"  Wichtigste Merkmale: {', '.join(imp.tail(3).index[::-1])}")
    except Exception as e:
        print(f"  (Wichtigkeitsgrafik übersprungen: {e})")


if __name__ == "__main__":
    main()
