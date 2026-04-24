"""TypedDicts and Pydantic models for product/catalog data."""

from __future__ import annotations

from typing import TypedDict


class ProductDict(TypedDict, total=False):
    category: str
    product_name: str
    price: float
    currency: str
    features: list[str]
    discount: str | None
    availability: str
    sku: str


class CatalogDict(TypedDict):
    company: str
    description: str
    products: list[ProductDict]


class NormalizedProduct(TypedDict, total=False):
    product_id: str
    company: str
    category: str
    product_name: str
    sku: str
    base_price: float
    discount_pct: int
    discount_type: str
    effective_price: float
    features: list[str]
    features_normalized: list[str]
    feature_count: int
    availability: str
    discount_text: str
    price_per_feature: float
