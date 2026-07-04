import argparse
import csv
import json
import re
from pathlib import Path

STANDARD_AA = set("ACDEFGHIKLMNPQRSTVWY")
REQUIRED_COLUMNS = ["Team_Name", "Seq_ID", "Sequence"]

def read_exclusion(path):
    if not path:
        return set()
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames and "Sequence" in reader.fieldnames:
            return {row["Sequence"].strip() for row in reader if row.get("Sequence")}
        f.seek(0)
        return {
            row[0].strip()
            for row in csv.reader(f)
            if row and row[0].strip() and row[0].strip() != "Sequence"
        }

def validate(path, exclusion=None):
    excluded = read_exclusion(exclusion)
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        errors = []
        if reader.fieldnames != REQUIRED_COLUMNS:
            errors.append(f"Header must be exactly {REQUIRED_COLUMNS}, found {reader.fieldnames}")
        rows = list(reader)
    if len(rows) > 6:
        errors.append(f"Too many sequences: {len(rows)}")
    seen_ids = set()
    seen_sequences = set()
    items = []
    for i, row in enumerate(rows, start=1):
        seq_id = row.get("Seq_ID", "")
        seq = row.get("Sequence", "").strip()
        row_errors = []
        if not seq_id:
            row_errors.append("missing Seq_ID")
        if seq_id in seen_ids:
            row_errors.append("duplicate Seq_ID")
        seen_ids.add(seq_id)
        if seq in seen_sequences:
            row_errors.append("duplicate Sequence")
        seen_sequences.add(seq)
        if not seq.startswith("M"):
            row_errors.append("sequence must start with M")
        if not (220 <= len(seq) <= 250):
            row_errors.append(f"length {len(seq)} outside 220-250")
        bad = sorted(set(seq) - STANDARD_AA)
        if bad:
            row_errors.append("invalid amino acid characters: " + "".join(bad))
        if "*" in seq:
            row_errors.append("contains stop character")
        if seq in excluded:
            row_errors.append("exact match in exclusion list")
        errors.extend([f"row {i}: {err}" for err in row_errors])
        items.append({"row": i, "Seq_ID": seq_id, "length": len(seq), "errors": row_errors})
    return {
        "path": str(path),
        "sequence_count": len(rows),
        "exclusion_checked": bool(excluded),
        "passed": not errors,
        "errors": errors,
        "items": items,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("submission_csv")
    parser.add_argument("--exclusion")
    parser.add_argument("--json-out")
    args = parser.parse_args()
    report = validate(args.submission_csv, args.exclusion)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
    raise SystemExit(0 if report["passed"] else 1)

if __name__ == "__main__":
    main()
