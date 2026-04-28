from __future__ import annotations

import csv
import json
from pathlib import Path


VECTOR_LENGTH = 512 * 18
_MODULE_DIR = Path(__file__).resolve().parent
_VECTORS_DIR = _MODULE_DIR / "vectors"
_METADATA_PATH = _VECTORS_DIR / "metaData.json"


def _load_metadata() -> list[dict]:
	with _METADATA_PATH.open("r", encoding="utf-8") as metadata_file:
		metadata = json.load(metadata_file)

	files = metadata.get("files")
	if not isinstance(files, list):
		raise ValueError("metaData.json must contain a 'files' list")

	return files


def _load_vector(csv_file_name: str) -> list[float]:
	csv_path = _VECTORS_DIR / csv_file_name
	if not csv_path.exists():
		raise FileNotFoundError(f"CSV file not found: {csv_file_name}")

	with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
		reader = csv.reader(csv_file)
		values: list[float] = []

		for row in reader:
			for value in row:
				stripped_value = value.strip()
				if stripped_value:
					values.append(float(stripped_value))

	if len(values) != VECTOR_LENGTH:
		raise ValueError(
			f"{csv_file_name} must contain exactly {VECTOR_LENGTH} numeric values, got {len(values)}"
		)

	return values


def load_vectors() -> list[dict]:
	ordered_vectors: list[dict] = []

	for entry in sorted(_load_metadata(), key=lambda item: item["id"]):
		if not isinstance(entry, dict):
			raise ValueError("Each metadata entry must be a dictionary")

		csv_file_name = entry.get("csv_file")
		range_low = entry.get("range_low")
		range_high = entry.get("range_high")
		entry_id = entry.get("id")

		if not isinstance(entry_id, int):
			raise ValueError("Each metadata entry must have an integer 'id'")
		if not isinstance(csv_file_name, str):
			raise ValueError(f"Metadata entry {entry_id} is missing a valid 'csv_file'")
		if not isinstance(range_low, (int, float)) or not isinstance(range_high, (int, float)):
			raise ValueError(f"Metadata entry {entry_id} must define numeric 'range_low' and 'range_high'")
		if range_low > range_high:
			raise ValueError(f"Metadata entry {entry_id} has range_low greater than range_high")

		ordered_vectors.append(
			{
				"low": float(range_low),
				"high": float(range_high),
				"vector": _load_vector(csv_file_name),
			}
		)

	return ordered_vectors
