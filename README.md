# Langfuse

Cost-analysis notebooks and a file backup of the Langfuse datasets.

## Layout

- `notebooks/` — cost analysis notebooks. They read `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` (or `LANGFUSE_BASE_URL`) from the environment.
- `Datasets/EU/` — datasets from the EU instance.
- `Datasets/US/Preprod/` — datasets from the US preprod instance.
- `Datasets/US/Prod/` — datasets from the US prod instance.
- `scripts/export_langfuse_datasets.py` — refreshes `Datasets/` from the three instances.

Dataset names that contain `/` are stored as nested folders. Each dataset folder has:

- `dataset.json` — dataset record, project, and item count
- `items.jsonl` — one dataset item per line

Dataset items are stored as JSON only. PDFs and other media files are not written into this repo.

`Datasets/catalog.json` is the index of the latest export.

## Instances

| Folder | Environment variables | Host | Project |
| --- | --- | --- | --- |
| `Datasets/EU` | `LANGFUSE_BASE_URL`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` | `eu-langfuse.kavida.ai` | `prod-agentUX` |
| `Datasets/US/Preprod` | `US_PREPROD_LANGFUSE_BASE_URL`, `US_PREPROD_LANGFUSE_PUBLIC_KEY`, `US_PREPROD_LANGFUSE_SECRET_KEY` | `langfuse.kavida.ai` | `preprod-agentux` |
| `Datasets/US/Prod` | `US_PROD_LANGFUSE_BASE_URL`, `US_PROD_LANGFUSE_PUBLIC_KEY`, `US_PROD_LANGFUSE_SECRET_KEY` | set by `US_PROD_LANGFUSE_BASE_URL` | whichever project those keys belong to |

Do not commit API keys. Keep them in the environment or a gitignored `.env` file.

## Refresh the backup

```bash
python scripts/export_langfuse_datasets.py
```

The script uses only the Python standard library. A missing credential set is recorded in that instance's `export-status.json` and the other instances are still exported.

## Latest export

Exported at 3:57 AM IST on 3 November 2026.

- EU (`prod-agentUX`): 56 datasets, 1,045 items. No dataset name contains SONIC.
- US Preprod (`preprod-agentux`): 4 AMSAFE Sales Champion datasets, 720 items, backed up at 5:03 AM IST on 3 November 2026. Header and line, each as `*_dataset_v0` and `gold_*_dataset`, under `Datasets/US/Preprod/AMSAFE/sales/sales_order_extractor/`. Every item is an AgentOps correction (`example_type` `difference`). No PDFs.
- US Prod: not exported. `US_PROD_LANGFUSE_BASE_URL`, `US_PROD_LANGFUSE_PUBLIC_KEY`, and `US_PROD_LANGFUSE_SECRET_KEY` are not set in this environment, so datasets on that instance, including SONIC, could not be read.
