# Colab vs Local

CompeteIQ runs identically in a local Python environment and in Google
Colab.  This document captures the differences the code abstracts away.

## Environment detection

```python
from competeiq.environment import is_colab, is_jupyter, is_local
```

- `is_colab()` — `True` when `google.colab` is importable
- `is_jupyter()` — `True` inside any IPython kernel
- `is_local()` — everything else

## Settings resolution

`Settings.load()` runs the same `.env` walk in both environments, then:

- **Local**: reads `./.env` or walks ancestors up to the repo root.
- **Colab**: additionally checks well-known Drive paths
  (`/content/drive/MyDrive/.env`, `.../CompeteIQ/.env`,
  `.../Colab Notebooks/.env`, `.../pwc-agenticai-capstone/.env`,
  `.../Agentic AI/.env`), then Colab `userdata` as a last resort.

## Recommended Colab cell

```python
!pip install -q langchain==0.3.14 langchain-openai==0.3.0 langfuse==2.57.1 \
    openai==1.59.6 chromadb==0.5.23 pyvis==0.3.2 gradio gradio_client pydantic-settings typer rich

from google.colab import drive
drive.mount('/content/drive')

import sys
sys.path.insert(0, '/content/drive/MyDrive/CompeteIQ/src')

from competeiq.system import EcommerceIntelligenceSystem
system = EcommerceIntelligenceSystem.build_default()
system.analyze_category("Wireless Headphones")
```

## Storage differences

| Resource | Local default | Colab recommendation |
|---|---|---|
| `COMPETEIQ_DATA_DIR` | `./datasets` | `/content/drive/MyDrive/CompeteIQ/datasets` |
| `COMPETEIQ_CHROMA_DIR` | `./.chroma` | `/content/drive/MyDrive/CompeteIQ/.chroma` (persistent) or leave mode=memory |
| `COMPETEIQ_CHROMA_MODE` | `persistent` | `memory` is usually fine for Colab sessions |

## UI in Colab

`competeiq ui --share` creates a gradio.live tunnel, which is the standard
way to expose the Gradio app from Colab.

## Notebook of origin

The original prototype lives at `Colab-Project/CompeteIQ.ipynb` and remains
functional; the packaged library imports the same catalogs verbatim so
output parity holds.
