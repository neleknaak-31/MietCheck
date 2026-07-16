"""Download the public source data used by MietCheck.

The script deliberately keeps raw files out of Git. It records a local manifest
with URL, retrieval timestamp, file size and SHA-256 hash so every analysis can
be traced to the exact bytes that were used.

Usage:
    python scripts/download_data.py
    python scripts/download_data.py --source zensus --force
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.request
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
MANIFEST_FILE = RAW_DIR / "source_manifest.json"
USER_AGENT = "MietCheck university research project/1.0"


@dataclass(frozen=True)
class Source:
    key: str
    filename: str
    url: str
    landing_page: str
    license: str
    citation: str
    minimum_bytes: int
    signature: bytes = b"PK"


SOURCES = {
    "zensus": Source(
        key="zensus",
        filename="zensus2022_rent_building_age_size.zip",
        url=(
            "https://www.destatis.de/static/DE/zensus/gitterdaten/"
            "Durchschnittliche_Nettokaltmiete_nach_Gebaeudealter_und_"
            "Wohnungsgroe%C3%9Fe.zip"
        ),
        landing_page=(
            "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/"
            "Bevoelkerung/Zensus2022/_publikationen.html"
        ),
        license="Datenlizenz Deutschland - Namensnennung - Version 2.0",
        citation=(
            "Statistische Aemter des Bundes und der Laender, Zensus 2022; eigene Verarbeitung."
        ),
        minimum_bytes=10_000_000,
    ),
    "zensus_population": Source(
        key="zensus_population",
        filename="zensus2022_population.zip",
        url=(
            "https://www.destatis.de/static/DE/zensus/gitterdaten/Zensus2022_Bevoelkerungszahl.zip"
        ),
        landing_page=(
            "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/"
            "Bevoelkerung/Zensus2022/_publikationen.html"
        ),
        license="Datenlizenz Deutschland - Namensnennung - Version 2.0",
        citation=(
            "Statistische Aemter des Bundes und der Laender, Zensus 2022; eigene Verarbeitung."
        ),
        minimum_bytes=10_000_000,
    ),
    "zensus_household_size": Source(
        key="zensus_household_size",
        filename="zensus2022_average_household_size.zip",
        url=(
            "https://www.destatis.de/static/DE/zensus/gitterdaten/"
            "Durchschnittliche_Haushaltsgroesse_in_Gitterzellen.zip"
        ),
        landing_page=(
            "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/"
            "Bevoelkerung/Zensus2022/_publikationen.html"
        ),
        license="Datenlizenz Deutschland - Namensnennung - Version 2.0",
        citation=(
            "Statistische Aemter des Bundes und der Laender, Zensus 2022; eigene Verarbeitung."
        ),
        minimum_bytes=10_000_000,
    ),
    "zensus_ownership": Source(
        key="zensus_ownership",
        filename="zensus2022_ownership_rate.zip",
        url=(
            "https://www.destatis.de/static/DE/zensus/gitterdaten/"
            "Eigentuemerquote_in_Gitterzellen.zip"
        ),
        landing_page=(
            "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/"
            "Bevoelkerung/Zensus2022/_publikationen.html"
        ),
        license="Datenlizenz Deutschland - Namensnennung - Version 2.0",
        citation=(
            "Statistische Aemter des Bundes und der Laender, Zensus 2022; eigene Verarbeitung."
        ),
        minimum_bytes=10_000_000,
    ),
    "zensus_vacancy": Source(
        key="zensus_vacancy",
        filename="zensus2022_vacancy_rate.zip",
        url=(
            "https://www.destatis.de/static/DE/zensus/gitterdaten/"
            "Leerstandsquote_in_Gitterzellen.zip"
        ),
        landing_page=(
            "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/"
            "Bevoelkerung/Zensus2022/_publikationen.html"
        ),
        license="Datenlizenz Deutschland - Namensnennung - Version 2.0",
        citation=(
            "Statistische Aemter des Bundes und der Laender, Zensus 2022; eigene Verarbeitung."
        ),
        minimum_bytes=8_000_000,
    ),
    "zensus_dwelling_area": Source(
        key="zensus_dwelling_area",
        filename="zensus2022_average_dwelling_area.zip",
        url=(
            "https://www.destatis.de/static/DE/zensus/gitterdaten/"
            "Durchschnittliche_Flaeche_je_Wohnung_in_Gitterzellen.zip"
        ),
        landing_page=(
            "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/"
            "Bevoelkerung/Zensus2022/_publikationen.html"
        ),
        license="Datenlizenz Deutschland - Namensnennung - Version 2.0",
        citation=(
            "Statistische Aemter des Bundes und der Laender, Zensus 2022; eigene Verarbeitung."
        ),
        minimum_bytes=10_000_000,
    ),
    "zensus_rent_count": Source(
        key="zensus_rent_count",
        filename="zensus2022_rent_and_dwelling_count.zip",
        url=(
            "https://www.destatis.de/static/DE/zensus/gitterdaten/"
            "Durchschnittliche_Nettokaltmiete_und_Anzahl_der_Wohnungen.zip"
        ),
        landing_page=(
            "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/"
            "Bevoelkerung/Zensus2022/_publikationen.html"
        ),
        license="Datenlizenz Deutschland - Namensnennung - Version 2.0",
        citation=(
            "Statistische Aemter des Bundes und der Laender, Zensus 2022; eigene Verarbeitung."
        ),
        minimum_bytes=8_000_000,
    ),
    "greix": Source(
        key="greix",
        filename="greix_city_metrics.xlsx",
        url=(
            "https://www.kielinstitut.de/fileadmin/Dateiverwaltung/"
            "IfW_Unit/Macroeconomics/GREIX/Mietpreisindex/"
            "City_metrics_public.xlsx"
        ),
        landing_page=(
            "https://www.kielinstitut.de/de/institut/forschungszentren/"
            "makrooekonomie/makrofinanzen/mietpreisindex/"
        ),
        license="Published research data; observe the mandatory source citation",
        citation="Kiel Institut fuer Weltwirtschaft auf Basis der VALUE Marktdatenbank.",
        minimum_bytes=500_000,
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_file(path: Path, source: Source) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    size = path.stat().st_size
    if size < source.minimum_bytes:
        raise ValueError(
            f"{source.key}: expected at least {source.minimum_bytes:,} bytes, received {size:,}"
        )
    with path.open("rb") as handle:
        signature = handle.read(len(source.signature))
    if signature != source.signature:
        raise ValueError(
            f"{source.key}: unexpected file signature {signature!r}; expected {source.signature!r}"
        )


def download(source: Source, force: bool) -> dict[str, object]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    destination = RAW_DIR / source.filename
    downloaded = False

    if force or not destination.exists():
        partial = destination.with_suffix(destination.suffix + ".part")
        partial.unlink(missing_ok=True)
        request = urllib.request.Request(
            source.url,
            headers={"User-Agent": USER_AGENT},
        )
        try:
            with (
                urllib.request.urlopen(request, timeout=120) as response,
                partial.open("wb") as output,
            ):
                shutil.copyfileobj(response, output, length=1024 * 1024)
            validate_file(partial, source)
            partial.replace(destination)
            downloaded = True
        except Exception:
            partial.unlink(missing_ok=True)
            raise

    validate_file(destination, source)
    now = datetime.now(UTC).replace(microsecond=0).isoformat()
    return {
        **asdict(source),
        "signature": source.signature.decode("ascii"),
        "path": str(destination.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "bytes": destination.stat().st_size,
        "sha256": sha256(destination),
        "verified_at_utc": now,
        "downloaded_in_this_run": downloaded,
    }


def load_manifest() -> dict[str, object]:
    if not MANIFEST_FILE.exists():
        return {"schema_version": 1, "sources": {}}
    return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))


def save_manifest(manifest: dict[str, object]) -> None:
    MANIFEST_FILE.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=["all", *SOURCES],
        default="all",
        help="Download one source or all sources (default: all).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace files that already exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected = SOURCES.values() if args.source == "all" else [SOURCES[args.source]]
    manifest = load_manifest()
    manifest_sources = manifest.setdefault("sources", {})

    for source in selected:
        print(f"[{source.key}] checking {source.url}")
        record = download(source, force=args.force)
        manifest_sources[source.key] = record
        state = "downloaded" if record["downloaded_in_this_run"] else "verified"
        print(
            f"[{source.key}] {state}: {record['path']} "
            f"({record['bytes']:,} bytes, sha256={record['sha256'][:12]}...)"
        )

    manifest["updated_at_utc"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    save_manifest(manifest)
    print(f"Manifest: {MANIFEST_FILE.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
