# Dataset Schema

CompeteIQ catalogs are JSON files, one per company, matching the
`CatalogDict` TypedDict in `competeiq.data.schemas`.

## Catalog

```jsonc
{
  "company": "Company X",
  "description": "Premium tech brand with cutting-edge features",
  "products": [ /* ProductDict, ProductDict, ... */ ]
}
```

## Product

```jsonc
{
  "category": "Wireless Headphones",
  "product_name": "Headphones X1",
  "price": 99.99,
  "currency": "USD",
  "features": ["Bluetooth 5.0", "Noise Cancelling", "20h Battery", "Fast Charge"],
  "discount": "10% off",        // optional; string or null
  "availability": "In Stock",   // "In Stock" | "Limited Stock" | "Out of Stock"
  "sku": "CX-HP-001"
}
```

### Normalised form (in-memory only)

After `TracedProductCatalogProcessor.normalize_product()` the dict becomes
`NormalizedProduct` — it adds:

- `product_id` (auto-assigned if absent)
- `company`
- `effective_price` (price after % discount)
- `discount_pct`, `discount_type` (e.g. `percentage`, `bundle`, `shipping`, `free`)
- `feature_count`
- `features_normalized` (abbreviations expanded: `ANC` → `noise cancelling` etc.)
- `price_per_feature`

Normalised products are not written back to disk; the persisted format is
always the raw `ProductDict`.

## Generating the reference set

```
competeiq datasets generate --output ./datasets --seed 42
```

This writes four files:

| File | Company | Strategy |
|---|---|---|
| `company_x.json` | Company X | Premium — verbatim from `competeiq.data.catalogs` |
| `company_y.json` | Company Y | Value — verbatim from `competeiq.data.catalogs` |
| `company_z.json` | Company Z | Tech innovator (premium-leaning, synth) |
| `company_w.json` | Company W | Budget leader (value-leaning, synth) |

Synthesised companies span six categories: Wireless Headphones, Smart
Watches, Portable Speakers, Laptops, Tablets, Earbuds.  The generator is
seeded → **byte-identical output** across runs with the same seed.

## Validation

```
competeiq datasets validate --data-dir ./datasets
```

Exits non-zero if any file fails the `ProductDict`/`CatalogDict` shape.

## Adding a new company

1. Write a new JSON file under `COMPETEIQ_DATA_DIR` following the schema above.
2. Run `competeiq datasets validate` to confirm it parses.
3. Re-run `competeiq index` (or restart) to rebuild the vector store.
4. The new company automatically flows through the processor + knowledge
   graph + orchestrator (all code is company-agnostic except the `our_company`
   setting).
