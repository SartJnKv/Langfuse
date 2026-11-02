# Dataset backup

Folders follow the Langfuse instance, then the dataset name:

```
Datasets/EU/<dataset name>/
Datasets/US/Preprod/<dataset name>/
Datasets/US/Prod/<dataset name>/
```

A `/` in a dataset name becomes a nested folder. `dataset.json` is the dataset record. `items.jsonl` is one item per line. PDF and other media files are not stored here.

See the repository README for the export time, counts, and how to refresh this backup.
