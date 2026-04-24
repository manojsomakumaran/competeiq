import json

import pytest

from competeiq.data.catalogs import COMPANY_X_CATALOG
from competeiq.data.loader import load_all_catalogs, load_catalog_file


@pytest.mark.unit
def test_load_catalog_file_roundtrip(tmp_path):
    path = tmp_path / "cat.json"
    path.write_text(json.dumps(COMPANY_X_CATALOG), encoding="utf-8")
    loaded = load_catalog_file(path)
    assert loaded["company"] == "Company X"
    assert len(loaded["products"]) == 6


@pytest.mark.unit
def test_load_catalog_file_rejects_invalid(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"not-a-catalog": true}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_catalog_file(path)


@pytest.mark.unit
def test_load_all_catalogs_discovers_json(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps(COMPANY_X_CATALOG), encoding="utf-8")
    catalogs = load_all_catalogs(tmp_path)
    assert len(catalogs) == 1
    assert catalogs[0]["company"] == "Company X"


@pytest.mark.unit
def test_load_all_catalogs_skips_malformed(tmp_path):
    (tmp_path / "good.json").write_text(json.dumps(COMPANY_X_CATALOG), encoding="utf-8")
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    catalogs = load_all_catalogs(tmp_path)
    assert len(catalogs) == 1


@pytest.mark.unit
def test_load_all_catalogs_missing_dir_falls_back_to_defaults(tmp_path):
    missing = tmp_path / "does-not-exist"
    catalogs = load_all_catalogs(missing)
    assert len(catalogs) >= 2  # Built-in Company X and Y
