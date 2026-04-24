"""Catalog EDA — build DataFrame + plot."""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from competeiq.data.schemas import CatalogDict

COMPANY_COLORS = {"Company X": "#3498db", "Company Y": "#e74c3c"}


def catalog_to_eda_rows(catalog: CatalogDict) -> list[dict]:
    rows: list[dict] = []
    for product in catalog["products"]:
        discount_str = product.get("discount") or ""
        m = re.search(r"(\d+)%", discount_str)
        discount_pct = int(m.group(1)) if m else 0
        base_price = float(product["price"])
        rows.append(
            {
                "company": catalog["company"],
                "category": product["category"],
                "product": product["product_name"],
                "base_price": base_price,
                "discount_pct": discount_pct,
                "effective_price": round(base_price * (1 - discount_pct / 100), 2),
                "feature_count": len(product.get("features", [])),
                "has_discount": product.get("discount") is not None,
            }
        )
    return rows


def build_eda_dataframe(catalogs: list[CatalogDict]) -> pd.DataFrame:
    rows: list[dict] = []
    for catalog in catalogs:
        rows.extend(catalog_to_eda_rows(catalog))
    return pd.DataFrame(rows)


def plot_eda(df: pd.DataFrame, output_path: Path | str = "ecommerce_eda.png") -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    colors = {c: COMPANY_COLORS.get(c, "#95a5a6") for c in df["company"].unique()}

    sns.barplot(
        data=df, x="product", y="effective_price", hue="company", palette=colors, ax=axes[0, 0]
    )
    axes[0, 0].set_title("Effective Price by Product")
    axes[0, 0].tick_params(axis="x", rotation=45)

    pivot = df.pivot_table(
        index="category", columns="company", values="effective_price", aggfunc="mean"
    )
    pivot.plot(kind="bar", color=[colors[c] for c in pivot.columns], ax=axes[0, 1])
    axes[0, 1].set_title("Average Effective Price by Category")
    axes[0, 1].tick_params(axis="x", rotation=30)

    avg = df.groupby("company", as_index=False)["feature_count"].mean()
    sns.barplot(
        data=avg,
        x="company",
        y="feature_count",
        hue="company",
        palette=colors,
        legend=False,
        ax=axes[1, 0],
    )
    axes[1, 0].set_title("Average Feature Count by Company")

    sns.scatterplot(
        data=df,
        x="effective_price",
        y="feature_count",
        hue="company",
        style="company",
        palette=colors,
        s=100,
        ax=axes[1, 1],
    )
    axes[1, 1].set_title("Price vs Feature Count")

    plt.tight_layout()
    out = Path(output_path)
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out
