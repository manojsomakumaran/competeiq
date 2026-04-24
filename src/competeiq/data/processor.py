"""Product catalog normalization + head-to-head comparison."""

from __future__ import annotations

import re
from typing import Any

from competeiq.data.schemas import CatalogDict, NormalizedProduct, ProductDict
from competeiq.tracing.langfuse_client import LangfuseProvider, get_provider


class TracedProductCatalogProcessor:
    """Normalize product catalogs, build feature vocabulary, and compare products."""

    _ABBREVIATION_MAP: dict[str, str] = {
        r"\banc\b": "noise cancelling",
        r"\badvanced anc\b": "advanced noise cancelling",
        r"\busb-c\b": "usb-c charging",
        r"\bbt\b": "bluetooth",
    }

    def __init__(self, provider: LangfuseProvider | None = None) -> None:
        self.processed_products: list[NormalizedProduct] = []
        self.feature_vocabulary: set[str] = set()
        self._provider = provider

    # ---------------- discount / features / product ----------------

    def parse_discount(self, discount_str: str | None) -> tuple[int, str]:
        if not discount_str:
            return (0, "none")
        pct_match = re.search(r"(\d+)%", discount_str)
        discount_pct = int(pct_match.group(1)) if pct_match else 0
        lower = discount_str.lower()
        if pct_match and ("free" in lower or "+" in lower):
            discount_type = "bundle"
        elif pct_match:
            discount_type = "percentage"
        elif "shipping" in lower:
            discount_type = "shipping"
        elif "free" in lower:
            discount_type = "free"
        else:
            discount_type = "other"
        return (discount_pct, discount_type)

    def normalize_features(self, features: list[str]) -> list[str]:
        normalized: list[str] = []
        for feature in features:
            norm = feature.lower().strip()
            for pattern, replacement in self._ABBREVIATION_MAP.items():
                norm = re.sub(pattern, replacement, norm)
            self.feature_vocabulary.add(norm)
            normalized.append(norm)
        return normalized

    def normalize_product(self, product: ProductDict, company: str) -> NormalizedProduct:
        discount_str = product.get("discount") or ""
        discount_pct, discount_type = self.parse_discount(discount_str)
        base_price = float(product.get("price", 0))
        effective_price = round(base_price * (1 - discount_pct / 100), 2)
        features = list(product.get("features", []))
        features_normalized = self.normalize_features(features)
        feature_count = len(features)
        price_per_feature = round(effective_price / feature_count, 4) if feature_count > 0 else 0.0
        return {
            "company": company,
            "category": product.get("category", ""),
            "product_name": product.get("product_name", ""),
            "sku": product.get("sku", ""),
            "base_price": base_price,
            "discount_pct": discount_pct,
            "discount_type": discount_type,
            "effective_price": effective_price,
            "features": features,
            "features_normalized": features_normalized,
            "feature_count": feature_count,
            "availability": product.get("availability", ""),
            "discount_text": discount_str,
            "price_per_feature": price_per_feature,
        }

    # ---------------- catalog-level ----------------

    def process_catalog(self, catalog: CatalogDict) -> list[NormalizedProduct]:
        company = catalog.get("company", "")
        results: list[NormalizedProduct] = []
        for idx, product in enumerate(catalog.get("products", [])):
            normalized = self.normalize_product(product, company)
            normalized["product_id"] = f"{company.replace(' ', '')}_{idx:03d}"
            self.processed_products.append(normalized)
            results.append(normalized)
        return results

    def process_catalog_with_tracing(self, catalog: CatalogDict) -> list[NormalizedProduct]:
        """Process a catalog with full Langfuse tracing, one span per product."""
        provider = self._provider or get_provider()
        company = catalog.get("company", "")
        products = list(catalog.get("products", []))
        trace = provider.langfuse.trace(
            name=f"catalog-processing-{company}",
            session_id=provider.session_id,
            tags=["catalog-processing", "week-2"],
            metadata={"company": company, "product_count": len(products)},
        )
        results: list[NormalizedProduct] = []
        for index, product in enumerate(products):
            product_id = f"{company.replace(' ', '')}_{index:03d}"
            span = trace.span(
                name=f"normalize-product-{product_id}",
                input={"product_name": product.get("product_name"), "sku": product.get("sku")},
            )
            normalized = self.normalize_product(product, company)
            normalized["product_id"] = product_id
            span.end(
                output={
                    "product_id": product_id,
                    "effective_price": normalized["effective_price"],
                    "feature_count": normalized["feature_count"],
                    "discount_type": normalized["discount_type"],
                }
            )
            self.processed_products.append(normalized)
            results.append(normalized)
        trace.update(
            output={
                "processed_count": len(results),
                "avg_price": round(sum(p["effective_price"] for p in results) / len(results), 2)
                if results
                else 0,
                "avg_features": round(sum(p["feature_count"] for p in results) / len(results), 2)
                if results
                else 0,
                "discounted_count": sum(1 for p in results if p["discount_pct"] > 0),
            }
        )
        return results

    # ---------------- comparison ----------------

    def compare_products(
        self, product_x: NormalizedProduct, product_y: NormalizedProduct
    ) -> dict[str, Any]:
        price_x = product_x["effective_price"]
        price_y = product_y["effective_price"]
        price_diff = round(price_x - price_y, 2)
        price_diff_pct = round((price_diff / price_y) * 100, 2) if price_y else 0.0
        if price_x < price_y:
            price_advantage = "X"
        elif price_y < price_x:
            price_advantage = "Y"
        else:
            price_advantage = "tie"

        features_x = {
            f.lower() for f in product_x.get("features_normalized", product_x.get("features", []))
        }
        features_y = {
            f.lower() for f in product_y.get("features_normalized", product_y.get("features", []))
        }

        fcount_x = product_x["feature_count"]
        fcount_y = product_y["feature_count"]
        if fcount_x > fcount_y:
            feature_advantage = "X"
        elif fcount_y > fcount_x:
            feature_advantage = "Y"
        else:
            feature_advantage = "tie"

        value_x = round((fcount_x / price_x) * 100, 4) if price_x else 0.0
        value_y = round((fcount_y / price_y) * 100, 4) if price_y else 0.0
        if value_x > value_y:
            value_advantage = "X"
        elif value_y > value_x:
            value_advantage = "Y"
        else:
            value_advantage = "tie"

        return {
            "category": product_x.get("category", ""),
            "product_x": product_x.get("product_name", ""),
            "product_y": product_y.get("product_name", ""),
            "price_x": price_x,
            "price_y": price_y,
            "price_diff": price_diff,
            "price_diff_pct": price_diff_pct,
            "price_advantage": price_advantage,
            "features_x": fcount_x,
            "features_y": fcount_y,
            "feature_advantage": feature_advantage,
            "value_x": value_x,
            "value_y": value_y,
            "value_advantage": value_advantage,
            "unique_to_x": sorted(features_x - features_y),
            "unique_to_y": sorted(features_y - features_x),
            "common_features": sorted(features_x & features_y),
        }
