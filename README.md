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

Dataset items are stored as JSON only. PDFs and other media files are not written into this repo. A configured Langfuse base URL inside an item is stored as the host only.

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

Exported at 6:08 AM IST on 3 November 2026. This refresh is US Prod. EU and US Preprod were not re-exported.

- EU (`prod-agentUX`): 57 datasets, 1,034 items. `SMD/sourcing/gold_dataset` is the combined sourcing gold set (226 items). The five variable datasets are still present as empty records.
- US Preprod (`preprod-agentux`): previous snapshot, 0 datasets.
- US Prod (`prod-agentux` on `langfuse.kavida.ai`): 51 datasets, 4,061 items. The 22 SONIC datasets are copied under `SONIC/procurement/...`. The original `SONIC / ...` names are still present. Empty folders remain for `SONIC/sales`, `SONIC/sourcing`, and `SONIC/ap`.
