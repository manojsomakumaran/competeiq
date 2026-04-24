"""Synthetic catalog generator.

Produces deterministic (seeded) catalogs for Companies X, Y, Z, W across six
categories (Wireless Headphones, Smart Watches, Portable Speakers, Laptops,
Tablets, Earbuds).  Companies X and Y are emitted verbatim from the built-in
constants for parity with the notebook; Z and W are synthesized.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from competeiq.data.catalogs import COMPANY_X_CATALOG, COMPANY_Y_CATALOG
from competeiq.data.schemas import CatalogDict

# ---------------------------------------------------------------------------
# Category templates — used to synthesise Companies Z and W.
# ---------------------------------------------------------------------------

CATEGORY_TEMPLATES: dict[str, dict] = {
    "Wireless Headphones": {
        "feature_pool": [
            "Bluetooth 5.2", "Bluetooth 5.3", "Advanced Noise Cancelling",
            "Transparency Mode", "30h Battery", "40h Battery", "Quick Charge",
            "Foldable", "Spatial Audio", "Hi-Res Audio", "USB-C", "Multipoint",
        ],
        "price_range": (79, 279),
    },
    "Smart Watches": {
        "feature_pool": [
            "Heart Rate", "GPS", "ECG", "SpO2", "7 Day Battery", "10 Day Battery",
            "Sleep Tracking", "Water Resistant", "100+ Workouts", "AMOLED Display",
            "LTE", "Voice Assistant",
        ],
        "price_range": (129, 499),
    },
    "Portable Speakers": {
        "feature_pool": [
            "Bluetooth 5.2", "Waterproof", "IP67 Rating", "Stereo Pairing",
            "Bass Boost", "LED Lights", "24h Battery", "20h Battery",
            "Mic Input", "Daisy Chain",
        ],
        "price_range": (59, 199),
    },
    "Laptops": {
        "feature_pool": [
            "16GB RAM", "32GB RAM", "1TB SSD", "512GB SSD", "14\" OLED",
            "15.6\" IPS", "Intel Core i7", "AMD Ryzen 7", "Backlit Keyboard",
            "Thunderbolt 4", "Wi-Fi 6E", "Dedicated GPU",
        ],
        "price_range": (799, 2199),
    },
    "Tablets": {
        "feature_pool": [
            "10.9\" Display", "12.4\" Display", "M2 Chip", "Snapdragon 8 Gen 2",
            "8GB RAM", "12GB RAM", "128GB Storage", "256GB Storage",
            "Stylus Support", "Keyboard Compatible", "5G", "Wi-Fi 6",
        ],
        "price_range": (299, 1099),
    },
    "Earbuds": {
        "feature_pool": [
            "Bluetooth 5.3", "Active Noise Cancelling", "Transparency Mode",
            "IPX4", "IPX7", "Wireless Charging", "6h Battery", "8h Battery",
            "Multipoint", "Spatial Audio", "Low Latency Mode",
        ],
        "price_range": (49, 249),
    },
}


COMPANY_PROFILES: dict[str, dict] = {
    "Company Z": {
        "description": "Tech-forward innovator brand",
        "sku_prefix": "CZ",
        "categories": ["Wireless Headphones", "Smart Watches", "Laptops", "Tablets"],
        "products_per_category": 2,
        "price_skew": 1.15,   # premium-leaning
    },
    "Company W": {
        "description": "Budget-friendly value brand",
        "sku_prefix": "CW",
        "categories": ["Wireless Headphones", "Portable Speakers", "Earbuds", "Tablets"],
        "products_per_category": 2,
        "price_skew": 0.80,   # value-leaning
    },
}


DISCOUNT_PATTERNS = ["10% off", "15% off", "20% off", "5% off + Free Case",
                    "Free Shipping", "Buy 1 Get 1 50% off", None, None]


def _synth_product(
    rng: random.Random,
    *,
    company: str,
    sku_prefix: str,
    category: str,
    index: int,
    price_skew: float,
) -> dict:
    template = CATEGORY_TEMPLATES[category]
    low, high = template["price_range"]
    base_price = round(rng.uniform(low, high) * price_skew, 2)
    feature_count = rng.randint(4, 6)
    features = rng.sample(template["feature_pool"], feature_count)
    discount = rng.choice(DISCOUNT_PATTERNS)
    availability = rng.choice(["In Stock", "In Stock", "In Stock", "Limited Stock"])
    tier = "Pro" if index % 2 else "Lite"
    return {
        "category": category,
        "product_name": f"{company.split()[-1]} {category.split()[0]} {tier} "
                       f"{index + 1}",
        "price": base_price,
        "currency": "USD",
        "features": features,
        "discount": discount,
        "availability": availability,
        "sku": f"{sku_prefix}-{category[:2].upper()}-{index + 1:03d}",
    }


def generate_company(company_name: str, seed: int) -> CatalogDict:
    """Synthesize one catalog for a non-builtin company."""
    profile = COMPANY_PROFILES[company_name]
    rng = random.Random(f"{company_name}-{seed}")
    products: list[dict] = []
    for category in profile["categories"]:
        for i in range(profile["products_per_category"]):
            products.append(
                _synth_product(
                    rng,
                    company=company_name,
                    sku_prefix=profile["sku_prefix"],
                    category=category,
                    index=i,
                    price_skew=profile["price_skew"],
                )
            )
    return {
        "company": company_name,
        "description": profile["description"],
        "products": products,
    }


def generate_all(output_dir: Path, *, seed: int = 42) -> list[Path]:
    """Write ``company_{x,y,z,w}.json`` into ``output_dir`` and return their paths."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    specs: list[tuple[str, CatalogDict]] = [
        ("company_x.json", COMPANY_X_CATALOG),
        ("company_y.json", COMPANY_Y_CATALOG),
        ("company_z.json", generate_company("Company Z", seed)),
        ("company_w.json", generate_company("Company W", seed)),
    ]
    written: list[Path] = []
    for filename, catalog in specs:
        path = output_dir / filename
        path.write_text(
            json.dumps(catalog, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        written.append(path)
    return written
