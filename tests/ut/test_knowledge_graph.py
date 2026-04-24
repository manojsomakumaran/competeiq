import pytest

from competeiq.graph.knowledge_graph import ProductKnowledgeGraph


@pytest.fixture()
def graph(sample_products) -> ProductKnowledgeGraph:
    g = ProductKnowledgeGraph()
    for p in sample_products:
        g.add_product(p)
    return g


@pytest.mark.unit
def test_taxonomy_seeded():
    g = ProductKnowledgeGraph()
    assert "Wireless Headphones" in g.graph
    assert "Company X" in g.graph
    assert "Bluetooth 5.0" in g.graph


@pytest.mark.unit
def test_add_product_creates_typed_edges(graph, sample_products):
    p = sample_products[0]
    pid = p["product_id"]
    assert graph.graph.has_edge(p["company"], pid)
    assert graph.graph.has_edge(pid, p["category"])
    for f in p["features"]:
        assert graph.graph.has_edge(pid, f)


@pytest.mark.unit
def test_competes_with_edges_are_cross_company(graph, sample_products):
    x1 = next(p for p in sample_products if p["product_name"] == "Headphones X1")
    z1 = next(p for p in sample_products if p["product_name"] == "Headphones Z1")
    assert graph.graph.has_edge(x1["product_id"], z1["product_id"])
    assert graph.graph.has_edge(z1["product_id"], x1["product_id"])


@pytest.mark.unit
def test_find_competing_products(graph, sample_products):
    x1 = next(p for p in sample_products if p["product_name"] == "Headphones X1")
    comps = graph.find_competing_products(x1["product_id"])
    assert comps  # non-empty


@pytest.mark.unit
def test_find_competing_products_missing_returns_empty(graph):
    assert graph.find_competing_products("nope") == []


@pytest.mark.unit
def test_get_unique_features(graph, sample_products):
    x1 = next(p for p in sample_products if p["product_name"] == "Headphones X1")
    z1 = next(p for p in sample_products if p["product_name"] == "Headphones Z1")
    out = graph.get_unique_features(x1["product_id"], z1["product_id"])
    assert "unique_to_ours" in out and "unique_to_competitor" in out and "common" in out


@pytest.mark.unit
def test_get_unique_features_missing_node(graph):
    out = graph.get_unique_features("missing", "also-missing")
    assert out == {"unique_to_ours": [], "unique_to_competitor": [], "common": []}
