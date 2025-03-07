import csv
import json
from pathlib import Path
from typing import LiteralString


def read_results(file_path: str | LiteralString | Path) -> dict:
    fp = Path(file_path)
    if fp.suffix == ".json":
        return read_json(fp)
    if fp.suffix == ".csv":
        return read_csv(fp)
    raise ValueError("Unsupported file type")


def read_json(file_path: str | LiteralString | Path) -> dict:
    with open(file_path, 'r', encoding='utf-8') as json_file:
        results = json.loads(json_file.read())
        return results


def read_csv(file_path: str | LiteralString | Path) -> dict:
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None)  # Get headers from the first row
        results = {}
        if headers:
            for h in list(headers):
                results[h] = []
            for row in reader:
                for i, v in enumerate(row):
                    results[headers[i]].append(v)

        return results
