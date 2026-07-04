# GFP Thermal-Brightness Design 2026

Team: `纳诺蔚来`  
Contact email: `joedan29@163.com`  
Public repository URL: upload this folder and fill in the resulting GitHub/GitLab/HuggingFace URL.

This repository contains reproducible materials for a six-sequence GFP
design submission targeting high initial fluorescence and high fluorescence
retention after 72 degrees C heat treatment.

## Files

- `outputs/submission_sequences.csv`: final three-column submission file.
- `data/candidate_design_notes.csv`: candidate names, mutation rationale, and risk notes.
- `scripts/generate_candidates.py`: deterministic candidate sequence generator.
- `scripts/validate_submission.py`: format and optional exclusion-list checker.
- `scripts/brightness_prior_model.py`: ProtT5 + RandomForest brightness-prior training outline.
- `validation_report.json`: validation result generated during packaging.

## Design Summary

The design pipeline combines a stable sfGFP-like scaffold, protein-language-model
embeddings, a supervised brightness-prior regressor, and thermal-stability
constraints. The final panel contains one conservative scaffold candidate,
three single-mutation candidates, and two double-mutation exploratory candidates.
This balances the low-brightness elimination rule against the Best Top-1 ranking format.

## Reproduce the Submission CSV

```bash
python scripts/generate_candidates.py --out outputs/submission_sequences.csv
python scripts/validate_submission.py outputs/submission_sequences.csv
```

When the official exclusion file is available, run:

```bash
python scripts/validate_submission.py outputs/submission_sequences.csv --exclusion Exclusion_List.csv
```

The competition requires a public repository link in the registration system.
Upload this repository folder, then use the resulting repository URL for that field.
