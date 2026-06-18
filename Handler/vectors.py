from __future__ import annotations
import csv
import json
from pathlib import Path
from initialImageSeeder import enqueue_face_generations, create_and_seed_initial_face_collection, is_initial_faces_seeded

fixedVectors = None

VECTOR_LENGTH = 9088
_MODULE_DIR = Path(__file__).resolve().parent
_VECTORS_DIR = _MODULE_DIR / "vectors"
_FEATURE_DIRECTIONS_DIR = _VECTORS_DIR / "featureDirections"
_METADATA_PATH = _FEATURE_DIRECTIONS_DIR / "metaData.json"
_FACES_DIR = _VECTORS_DIR / "faces"
_FACES_METADATA_PATH = _FACES_DIR / "metaData.json"


def _load_metadata() -> list[dict]:
	with _METADATA_PATH.open("r", encoding="utf-8") as metadata_file:
		metadata = json.load(metadata_file)

	files = metadata.get("files")
	if not isinstance(files, list):
		raise ValueError("metaData.json must contain a 'files' list")

	return files


def _load_vector(csv_file_name: str, directory: Path = _FEATURE_DIRECTIONS_DIR) -> list[float]:
	csv_path = directory / csv_file_name
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
				"vector": _load_vector(csv_file_name, _FEATURE_DIRECTIONS_DIR),
			}
		)

	return ordered_vectors


async def load_face_vectors(
	gender: str | None = None,
	age: str | None = None,
) :
	with _FACES_METADATA_PATH.open("r", encoding="utf-8") as f:
		metadata = json.load(f)

	files = metadata.get("files")
	if not isinstance(files, list):
		raise ValueError("faces/metaData.json must contain a 'files' list")

	if await is_initial_faces_seeded(len(files)):
		return

	result: list[dict] = []

	for entry in sorted(files, key=lambda item: item["id"]):
		if not isinstance(entry, dict):
			raise ValueError("Each metadata entry must be a dictionary")

		entry_id = entry.get("id")
		csv_file_name = entry.get("csv_file")
		entry_gender = entry.get("gender")
		entry_age = entry.get("age")

		if not isinstance(entry_id, int):
			raise ValueError("Each metadata entry must have an integer 'id'")
		if not isinstance(csv_file_name, str):
			raise ValueError(f"Metadata entry {entry_id} is missing a valid 'csv_file'")
		if not isinstance(entry_gender, str) or not isinstance(entry_age, str):
			raise ValueError(f"Metadata entry {entry_id} must define string 'gender' and 'age'")

		if gender is not None and entry_gender != gender:
			continue
		if age is not None and entry_age != age:
			continue

		result.append({
			"vector": _load_vector(csv_file_name, _FACES_DIR),
			"gender": entry_gender,
			"age": entry_age,
		})

	image_ids = await enqueue_face_generations(result)

	for entry, image_id in zip(result, image_ids):
		entry["image_id"] = image_id
	
	await create_and_seed_initial_face_collection(result)

def get_fixed_vectors():
    if fixedVectors is None:
        raise RuntimeError("Vectors not loaded yet")
    return fixedVectors