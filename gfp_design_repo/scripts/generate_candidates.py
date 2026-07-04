import argparse
import csv
import re
from pathlib import Path

TEAM_NAME = '纳诺蔚来'

SFGFP_CORE = 'MSKGEELFTGVVPILVELDGDVNGHKFSVRGEGEGDATNGKLTLKFICTTGKLPVPWPTLVTTLTYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTISFKDDGTYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYITADKQKNGIKANFKIRHNVEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSVLSKDPNEKRDHMVLLEFVTAAGITHGMDELYK'

CANDIDATE_MUTATIONS = [
    ("1", []),
    ("2", ["K162I"]),
    ("3", ["N198P"]),
    ("4", ["K140L"]),
    ("5", ["E132R", "N198P"]),
    ("6", ["Y106R", "K162I"]),
]

def mutate(sequence, mutations):
    seq = list(sequence)
    for mutation in mutations:
        m = re.fullmatch(r"([A-Z])(\d+)([A-Z])", mutation)
        if not m:
            raise ValueError(f"Bad mutation notation: {mutation}")
        old, pos_s, new = m.groups()
        pos = int(pos_s)
        if seq[pos - 1] != old:
            raise ValueError(f"{mutation} expected {old} at {pos}, found {seq[pos - 1]}")
        seq[pos - 1] = new
    return "".join(seq)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="outputs/submission_sequences.csv")
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Team_Name", "Seq_ID", "Sequence"])
        writer.writeheader()
        for seq_id, mutations in CANDIDATE_MUTATIONS:
            writer.writerow({
                "Team_Name": TEAM_NAME,
                "Seq_ID": seq_id,
                "Sequence": mutate(SFGFP_CORE, mutations),
            })
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
