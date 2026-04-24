# CLI Usage

The `competeiq` CLI is installed as a console script by the package.  During
development you can also run `python -m competeiq.cli ...`.

```
competeiq --help
```

## Commands

### `status`
Print system status (products indexed, categories, vector-store mode, graph stats).

```
competeiq status
```

### `analyze <category>`
Run the multi-agent competitive analysis and print summary + marketing headline.

```
competeiq analyze "Wireless Headphones"
```

### `search <query> [--n 5]`
Semantic product search against the Chroma collection.

```
competeiq search "waterproof speaker" --n 3
```

### `compare <category>`
Tabular price comparison across companies for a category.

```
competeiq compare "Smart Watches"
```

### `index`
Force rebuild the persistent vector-store collection.

```
competeiq index
```

### `ui [--host 127.0.0.1] [--port 7860] [--share]`
Launch the Gradio UI (same as the `competeiq-ui` console script).

```
competeiq ui --port 7860
```

### `datasets`
Manage catalog JSON files.

```
competeiq datasets generate --output ./datasets --seed 42
competeiq datasets validate --data-dir ./datasets
```

### `graph`
Knowledge-graph ops.

```
competeiq graph export --output ./product_knowledge_graph.png
competeiq graph dump
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Validation failure (e.g. malformed catalog) or unhandled error |
| 2 | Invalid CLI arguments (Typer default) |
