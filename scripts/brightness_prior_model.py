"""Brightness-prior model outline for reproducible sequence scoring.

This file documents the ProtT5 + RandomForest brightness-prior workflow. It is not
required for validating the final CSV, but keeps the modeling path
reproducible for reviewers who want to retrain the brightness prior.
"""

import argparse
import re

import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from transformers import T5EncoderModel, T5Tokenizer

AVGFP = (
    "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTLS"
    "YGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDF"
    "KEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLP"
    "DNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK"
)

def apply_mutations(sequence, mutation_text):
    seq = list(sequence)
    if mutation_text == "WT":
        return sequence
    for mutation in str(mutation_text).split(":"):
        old = mutation[0]
        new = mutation[-1]
        pos = int(mutation[1:-1])
        if pos >= len(seq) or seq[pos] != old:
            continue
        seq[pos] = new
    return "".join(seq)

def embed_sequences(sequences, model_name, batch_size):
    tokenizer = T5Tokenizer.from_pretrained(model_name, do_lower_case=False)
    model = T5EncoderModel.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device).eval()
    embeddings = []
    for start in range(0, len(sequences), batch_size):
        batch = [" ".join(list(re.sub(r"[UZOB]", "X", s))) for s in sequences[start:start + batch_size]]
        encoded = tokenizer.batch_encode_plus(batch, add_special_tokens=True, padding=True)
        input_ids = torch.tensor(encoded["input_ids"]).to(device)
        attention_mask = torch.tensor(encoded["attention_mask"]).to(device)
        with torch.no_grad():
            out = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        for i in range(out.shape[0]):
            embeddings.append(out[i].mean(dim=0).cpu().numpy())
    return np.vstack(embeddings)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gfp-data", required=True)
    parser.add_argument("--model-name", default="Rostlab/prot_t5_xl_uniref50")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--model-out", default="random_forest_regressor.pkl")
    args = parser.parse_args()

    df = pd.read_excel(args.gfp_data).fillna("")
    df["sequence"] = df["aaMutations"].map(lambda x: apply_mutations(AVGFP, x))
    X = embed_sequences(df["sequence"].tolist(), args.model_name, args.batch_size)
    y = df["Brightness"].to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(X_train, y_train)
    pred = regressor.predict(X_test)
    print({"mse": float(mean_squared_error(y_test, pred)), "n": len(df)})
    joblib.dump(regressor, args.model_out)

if __name__ == "__main__":
    main()
