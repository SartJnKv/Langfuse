#!/usr/bin/env python3
"""Export every dataset from the configured Langfuse instances.

Credentials come from the environment. Nothing in this script prints keys.

  EU         LANGFUSE_BASE_URL, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY
  US Preprod US_PREPROD_LANGFUSE_BASE_URL, US_PREPROD_LANGFUSE_PUBLIC_KEY, US_PREPROD_LANGFUSE_SECRET_KEY
  US Prod    US_PROD_LANGFUSE_BASE_URL, US_PROD_LANGFUSE_PUBLIC_KEY, US_PROD_LANGFUSE_SECRET_KEY

Layout:

  Datasets/EU/<dataset name as folders>/dataset.json
  Datasets/EU/<dataset name as folders>/items.jsonl
  Datasets/US/Preprod/...
  Datasets/US/Prod/...
"""

from __future__ import annotations

import base64
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT / "Datasets"

INSTANCES = [
    {
        "label": "EU",
        "region": "EU",
        "subdir": None,
        "base_env": "LANGFUSE_BASE_URL",
        "public_env": "LANGFUSE_PUBLIC_KEY",
        "secret_env": "LANGFUSE_SECRET_KEY",
    },
    {
        "label": "US Preprod",
        "region": "US",
        "subdir": "Preprod",
        "base_env": "US_PREPROD_LANGFUSE_BASE_URL",
        "public_env": "US_PREPROD_LANGFUSE_PUBLIC_KEY",
        "secret_env": "US_PREPROD_LANGFUSE_SECRET_KEY",
    },
    {
        "label": "US Prod",
        "region": "US",
        "subdir": "Prod",
        "base_env": "US_PROD_LANGFUSE_BASE_URL",
        "public_env": "US_PROD_LANGFUSE_PUBLIC_KEY",
        "secret_env": "US_PROD_LANGFUSE_SECRET_KEY",
    },
]


def instance_root(spec: dict) -> Path:
    path = DATASETS_ROOT / spec["region"]
    if spec["subdir"]:
        path = path / spec["subdir"]
    return path


def dataset_dir(root: Path, name: str) -> Path:
    normalized = name.replace(" / ", "/")
    parts = [part.strip() for part in normalized.split("/")]
    if not parts or any(not part or part in {".", ".."} or "/" in part or "\\" in part for part in parts):
        raise ValueError(f"Unsafe dataset name: {name!r}")
    return root.joinpath(*parts)


class Client:
    def __init__(self, base_url: str, public_key: str, secret_key: str):
        self.base_url = base_url.rstrip("/")
        token = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
        self.headers = {"Authorization": f"Basic {token}", "Accept": "application/json"}

    @property
    def host(self) -> str:
        return urllib.parse.urlparse(self.base_url).hostname or self.base_url

    def get(self, path: str, params: dict | None = None):
        query = ("?" + urllib.parse.urlencode(params)) if params else ""
        request = urllib.request.Request(self.base_url + path + query, headers=self.headers)
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.load(response)


def list_all(client: Client, path: str, params: dict) -> list:
    page = 1
    rows = []
    while True:
        payload = client.get(path, {**params, "page": page, "limit": 100})
        batch = payload.get("data") or []
        rows.extend(batch)
        meta = payload.get("meta") or {}
        total_pages = meta.get("totalPages") or 0
        if page >= total_pages or not batch:
            break
        page += 1
    return rows


MEDIA_EXTENSIONS = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "text/plain": ".txt",
    "text/csv": ".csv",
}


def media_filename(media: dict) -> str:
    media_id = media.get("mediaId") or ""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", media_id):
        raise ValueError(f"Unexpected media id: {media_id!r}")
    return media_id + MEDIA_EXTENSIONS.get(media.get("contentType") or "", "")


def store_media(client_root: Path, item: dict, downloaded: dict[str, str]) -> None:
    """Save referenced files and drop expiring URLs, which carry session tokens."""
    for reference in item.get("mediaReferences") or []:
        media = reference.get("media") or {}
        media_id = media.get("mediaId")
        if not media_id:
            continue
        filename = media_filename(media)
        destination = client_root / "media" / filename
        if media_id not in downloaded:
            url = media.get("url")
            if not url:
                raise RuntimeError(f"Media {media_id} has no download URL")
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(destination.suffix + ".partial")
            try:
                with urllib.request.urlopen(url, timeout=120) as response:
                    temporary.write_bytes(response.read())
            except Exception as error:
                temporary.unlink(missing_ok=True)
                raise RuntimeError(f"Failed to download media {media_id}: {type(error).__name__}") from None
            temporary.replace(destination)
            downloaded[media_id] = str(destination.relative_to(DATASETS_ROOT))
        media.pop("url", None)
        media["localFile"] = downloaded[media_id]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def remove_stale_datasets(root: Path, expected: set[Path]) -> list[str]:
    removed = []
    if not root.exists():
        return removed
    for dataset_file in root.rglob("dataset.json"):
        folder = dataset_file.parent
        if folder not in expected:
            shutil.rmtree(folder)
            removed.append(str(folder.relative_to(DATASETS_ROOT)))
    # Drop directories that became empty after a dataset was removed.
    for directory in sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda p: len(p.parts), reverse=True):
        if directory == root:
            continue
        if not any(directory.iterdir()):
            directory.rmdir()
    return removed


def export_instance(spec: dict, exported_at: str) -> dict:
    root = instance_root(spec)
    missing = [spec[key] for key in ("base_env", "public_env", "secret_env") if not os.environ.get(spec[key])]
    if missing:
        root.mkdir(parents=True, exist_ok=True)
        status = {
            "instance": spec["label"],
            "exportedAt": exported_at,
            "status": "not_exported",
            "reason": "Missing environment variables: " + ", ".join(missing),
        }
        write_json(root / "export-status.json", status)
        return {"label": spec["label"], "ok": False, "datasetCount": 0, "itemCount": 0, "status": status}

    root.mkdir(parents=True, exist_ok=True)

    client = Client(
        os.environ[spec["base_env"]],
        os.environ[spec["public_env"]],
        os.environ[spec["secret_env"]],
    )
    projects = client.get("/api/public/projects").get("data") or []
    project = projects[0] if projects else {}
    datasets = list_all(client, "/api/public/v2/datasets", {})
    expected: set[Path] = set()
    catalog = []
    item_count = 0
    media_datasets = []
    downloaded: dict[str, str] = {}

    for dataset in datasets:
        name = dataset["name"]
        items = list_all(client, "/api/public/dataset-items", {"datasetName": name})
        for item in items:
            if item.get("mediaReferences"):
                store_media(root, item, downloaded)
        folder = dataset_dir(root, name)
        expected.add(folder)
        record = {
            "instance": spec["label"],
            "host": client.host,
            "project": {"id": project.get("id"), "name": project.get("name")},
            "dataset": dataset,
            "itemCount": len(items),
            "exportedAt": exported_at,
        }
        write_json(folder / "dataset.json", record)
        lines = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in items]
        (folder / "items.jsonl").write_text(("\n".join(lines) + ("\n" if lines else "")), encoding="utf-8")
        item_count += len(items)
        if any(item.get("mediaReferences") for item in items):
            media_datasets.append(name)
        catalog.append(
            {
                "name": name,
                "id": dataset.get("id"),
                "itemCount": len(items),
                "updatedAt": dataset.get("updatedAt"),
                "path": str(folder.relative_to(DATASETS_ROOT)),
            }
        )

    removed = remove_stale_datasets(root, expected)
    media_dir = root / "media"
    if media_dir.exists():
        referenced = set(downloaded)
        for existing in media_dir.iterdir():
            if existing.stem not in referenced and existing.is_file():
                existing.unlink()
                removed.append(str(existing.relative_to(DATASETS_ROOT)))
    status_path = root / "export-status.json"
    if datasets:
        if status_path.exists():
            status_path.unlink()
    else:
        write_json(
            status_path,
            {
                "instance": spec["label"],
                "host": client.host,
                "project": {"id": project.get("id"), "name": project.get("name")},
                "exportedAt": exported_at,
                "status": "exported",
                "datasetCount": 0,
                "itemCount": 0,
            },
        )
    summary = {
        "label": spec["label"],
        "ok": True,
        "host": client.host,
        "project": {"id": project.get("id"), "name": project.get("name")},
        "datasetCount": len(datasets),
        "itemCount": item_count,
        "removedStale": removed,
        "datasetsWithMedia": media_datasets,
        "mediaFiles": len(downloaded),
        "datasets": catalog,
    }
    print(
        f"{spec['label']}: {len(datasets)} datasets, {item_count} items, host={client.host}",
        file=sys.stderr,
    )
    return summary


def main() -> int:
    exported_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summaries = [export_instance(spec, exported_at) for spec in INSTANCES]
    write_json(
        DATASETS_ROOT / "catalog.json",
        {"exportedAt": exported_at, "instances": summaries},
    )
    failed = [item["label"] for item in summaries if not item["ok"]]
    if failed:
        print("Not exported: " + ", ".join(failed), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
