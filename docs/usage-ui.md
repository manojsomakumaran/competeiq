# Web UI Usage

The Gradio UI is a Blocks app with four tabs.  Launch it via:

```
competeiq ui                 # default http://127.0.0.1:7860
competeiq-ui                 # equivalent console script
competeiq ui --share         # public gradio.live link
python -m competeiq.ui.gradio_app
```

## Tabs

### 1. Category Analysis
Pick a category from the dropdown and click **Run Category Analysis**.  Output includes:
- Overall position (PREMIUM / COMPETITIVE / VALUE / FEATURE_LEADER / FEATURE_GAP / UNKNOWN)
- Key findings bullet list
- Priority actions (top 5, deduped)
- Marketing headline

### 2. Product Search
Free-text semantic search.  Returns the top 5 matches with company, price,
similarity (`1 - distance`, clamped to [0, 1]) and availability.

### 3. Price Comparison
Select a category; the tab renders a sortable markdown table with:
`company, product_name, base_price, effective_price, discount_pct,
feature_count, availability, sku, price_gap_vs_category_avg`.

### 4. System Status
Session ID, our-company label, catalog counts, categories, vector-store
mode, and knowledge-graph node/edge counts.

## Configuration

Bind host / port and share-link behaviour come from `Settings`
(`GRADIO_SERVER_NAME`, `GRADIO_SERVER_PORT`, `GRADIO_SHARE`) and are
overridable via CLI flags: `competeiq ui --host 0.0.0.0 --port 7860 --share`.
