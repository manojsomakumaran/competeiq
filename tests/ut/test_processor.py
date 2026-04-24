import pytest

from competeiq.data.processor import TracedProductCatalogProcessor


@pytest.fixture()
def processor(fake_provider):
    return TracedProductCatalogProcessor(provider=fake_provider)


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,pct,kind",
    [
        (None, 0, "none"),
        ("", 0, "none"),
        ("10% off", 10, "percentage"),
        ("5% off + Free Case", 5, "bundle"),
        ("Free Shipping", 0, "shipping"),
        ("Free Case", 0, "free"),
        ("Mystery deal", 0, "other"),
    ],
)
def test_parse_discount(processor, text, pct, kind):
    assert processor.parse_discount(text) == (pct, kind)


@pytest.mark.unit
def test_normalize_features_expands_abbreviations(processor):
    out = processor.normalize_features(["ANC", "BT", "USB-C", "Advanced ANC"])
    assert "noise cancelling" in out
    assert "bluetooth" in out
    assert "usb-c charging" in out
    assert "advanced noise cancelling" in out


@pytest.mark.unit
def test_normalize_product_price_math(processor, sample_catalogs):
    product = sample_catalogs[0]["products"][0]  # Headphones X1, $99.99, 10% off
    normalized = processor.normalize_product(product, "Company X")
    assert normalized["discount_pct"] == 10
    assert normalized["effective_price"] == pytest.approx(89.99, abs=0.01)
    assert normalized["feature_count"] == 4


@pytest.mark.unit
def test_process_catalog_with_tracing_emits_spans(processor, sample_catalogs, fake_provider):
    catalog = sample_catalogs[0]
    results = processor.process_catalog_with_tracing(catalog)
    assert len(results) == 6
    trace = fake_provider.langfuse.traces[-1]
    assert len(trace.spans) == 6
    assert trace.updates  # trace.update was called


@pytest.mark.unit
def test_compare_products_tie_and_advantages(processor, sample_products):
    # Find two products in same category
    headphones = [p for p in sample_products if p["category"] == "Wireless Headphones"]
    a, b = headphones[0], headphones[-1]  # X1 vs Z2
    cmp = processor.compare_products(a, b)
    assert cmp["price_advantage"] in {"X", "Y", "tie"}
    assert cmp["feature_advantage"] in {"X", "Y", "tie"}
    assert "unique_to_x" in cmp and "unique_to_y" in cmp and "common_features" in cmp


@pytest.mark.unit
def test_compare_products_tie_when_equal(processor):
    p = {
        "category": "Cat",
        "product_name": "A",
        "effective_price": 100.0,
        "feature_count": 3,
        "features": ["f1", "f2", "f3"],
        "features_normalized": ["f1", "f2", "f3"],
    }
    q = {**p, "product_name": "B"}
    cmp = processor.compare_products(p, q)
    assert cmp["price_advantage"] == "tie"
    assert cmp["feature_advantage"] == "tie"
    assert cmp["value_advantage"] == "tie"
