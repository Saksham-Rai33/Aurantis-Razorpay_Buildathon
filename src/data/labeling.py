import pandas as pd
import numpy as np

LABEL_THRESHOLD = 6

DISPOSABLE_DOMAINS = {
    "guerrillamail.com", "mailinator.com", "tempmail.com",
    "yopmail.com", "trashmail.com", "maildrop.cc"
}

HIGH_RISK_PRODUCTS = {"H", "S", "R"}


def score_transaction(row):
    score = 0

    # Signal 1: Address mismatch (+2)
    if pd.notna(row.get("addr1")) and pd.notna(row.get("addr2")):
        if row["addr1"] != row["addr2"]:
            score += 2

    # Signal 2: Disposable email (+2)
    domain = str(row.get("P_emaildomain", "")).lower()
    if domain in DISPOSABLE_DOMAINS:
        score += 2

    # Signal 3: High risk product (+2)
    if row.get("ProductCD") in HIGH_RISK_PRODUCTS:
        score += 2

    # Signal 4: High amount (+1)
    amt = row.get("TransactionAmt", 0)
    if pd.notna(amt) and amt >= 500:
        score += 1

    # Signal 5: Round amount (+1)
    if pd.notna(amt) and amt > 0 and amt % 50 == 0:
        score += 1

    # Signal 6: Night transaction (+1)
    dt = row.get("TransactionDT", 0)
    if pd.notna(dt):
        tod = int(dt) % 86400
        if tod >= 72000 or tod <= 7200:
            score += 1

    # Signal 7: Email domain mismatch (+1)
    p = str(row.get("P_emaildomain", ""))
    r = str(row.get("R_emaildomain", ""))
    if p and r and p != r and p != "nan" and r != "nan":
        score += 1

    # Signal 8: Discover card (+1)
    if str(row.get("card4", "")).lower() == "discover":
        score += 1

    return score


def generate_labels(df):
    print("Scoring transactions...")
    df = df.copy()
    df["risk_score"] = df.apply(score_transaction, axis=1)
    df["return_risk"] = (df["risk_score"] >= LABEL_THRESHOLD).astype(int)

    total = len(df)
    positives = df["return_risk"].sum()
    print(f"Total transactions: {total:,}")
    print(f"Return risk = 1:    {positives:,} ({positives/total:.2%})")
    print(f"Return risk = 0:    {total - positives:,}")

    return df


if __name__ == "__main__":
    from src.data.loader import load_raw
    df = load_raw()
    df = generate_labels(df)
    print(df[["TransactionID", "risk_score", "return_risk"]].head(10))