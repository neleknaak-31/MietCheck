from pathlib import Path

import pytest

from scripts.download_data import SOURCES, Source, sha256, validate_file


def test_source_filenames_are_unique() -> None:
    filenames = [source.filename for source in SOURCES.values()]
    assert len(filenames) == len(set(filenames))


def test_all_sources_use_https() -> None:
    assert all(source.url.startswith("https://") for source in SOURCES.values())
    assert all(source.landing_page.startswith("https://") for source in SOURCES.values())


def test_validate_file_accepts_expected_signature(tmp_path: Path) -> None:
    path = tmp_path / "source.zip"
    path.write_bytes(b"PK" + b"x" * 20)
    source = Source(
        key="test",
        filename=path.name,
        url="https://example.test/source.zip",
        landing_page="https://example.test/",
        license="test",
        citation="test",
        minimum_bytes=10,
    )

    validate_file(path, source)
    assert len(sha256(path)) == 64


def test_validate_file_rejects_html_error_page(tmp_path: Path) -> None:
    path = tmp_path / "source.zip"
    path.write_bytes(b"<!doctype html>not a zip file")
    source = Source(
        key="test",
        filename=path.name,
        url="https://example.test/source.zip",
        landing_page="https://example.test/",
        license="test",
        citation="test",
        minimum_bytes=10,
    )

    with pytest.raises(ValueError, match="unexpected file signature"):
        validate_file(path, source)
