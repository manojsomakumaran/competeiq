import json

import pytest

from competeiq.data.generator import generate_all, generate_company


@pytest.mark.unit
def test_generate_all_writes_four_files(tmp_path):
    paths = generate_all(tmp_path, seed=42)
    assert len(paths) == 4
    names = {p.name for p in paths}
    assert {"company_x.json", "company_y.json", "company_z.json", "company_w.json"} == names


@pytest.mark.unit
def test_generate_all_is_deterministic_by_seed(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    paths_a = generate_all(a, seed=42)
    paths_b = generate_all(b, seed=42)
    for pa, pb in zip(sorted(paths_a), sorted(paths_b), strict=False):
        assert pa.read_bytes() == pb.read_bytes()


@pytest.mark.unit
def test_generate_company_synthesises_expected_schema():
    catalog = generate_company("Company Z", seed=42)
    assert catalog["company"] == "Company Z"
    assert catalog["products"]
    for p in catalog["products"]:
        assert {"category", "product_name", "price", "currency", "features", "sku"} <= p.keys()
        assert isinstance(p["features"], list)
        assert p["price"] > 0


@pytest.mark.unit
def test_generate_all_json_files_parse(tmp_path):
    paths = generate_all(tmp_path, seed=1)
    for p in paths:
        data = json.loads(p.read_text(encoding="utf-8"))
        assert "company" in data and "products" in data
