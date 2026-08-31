import pandas as pd
import numpy as np

DISPOSABLE_DOMAINS = {
    "guerrillamail.com", "mailinator.com", "tempmail.com",
    "yopmail.com", "trashmail.com", "maildrop.cc"
}


def add_amount_features(df):
    df["amt_log"] = np.log1p(df["TransactionAmt"].fillna(0))
    df["amt_is_round"] = ((df["TransactionAmt"] % 50 == 0) & (df["TransactionAmt"] > 0)).astype(int)
    df["amt_is_high"] = (df["TransactionAmt"] >= 500).astype(int)
    return df


def add_address_features(df):
    df["addr_mismatch"] = (
        df["addr1"].notna() & df["addr2"].notna() & (df["addr1"] != df["addr2"])
    ).astype(int)
    return df


def add_email_features(df):
    p = df["P_emaildomain"].fillna("").str.lower()
    r = df["R_emaildomain"].fillna("").str.lower()
    df["email_disposable"] = p.isin(DISPOSABLE_DOMAINS).astype(int)
    df["email_mismatch"] = ((p != r) & (p != "") & (r != "")).astype(int)
    return df


def add_time_features(df):
    tod = df["TransactionDT"].fillna(0).astype(int) % 86400
    df["tod_hour"] = tod // 3600
    df["is_night"] = ((tod >= 72000) | (tod <= 7200)).astype(int)
    return df


def add_velocity_features(df):
    df["card1_freq"] = df["card1"].map(df["card1"].value_counts())
    df["addr1_freq"] = df["addr1"].map(df["addr1"].value_counts())
    df["card1_freq_log"] = np.log1p(df["card1_freq"].fillna(0))
    df["addr1_freq_log"] = np.log1p(df["addr1_freq"].fillna(0))
    return df


def run_pipeline(df):
    print("Running feature engineering...")
    df = add_amount_features(df)
    df = add_address_features(df)
    df = add_email_features(df)
    df = add_time_features(df)
    df = add_velocity_features(df)
    print(f"Done. Shape: {df.shape}")
    return df


FEATURE_COLS = [
    "amt_log",
    "amt_is_high",
    "card1_freq_log",
    "addr1_freq_log",
    "TransactionAmt",
    "C1", "C2", "C3", "C4", "C5",
    "C6", "C7", "C8", "C9", "C10",
    "D1", "D2", "D3", "D4", "D5",
    "V1", "V2", "V3", "V4", "V5",
    "V6", "V7", "V8", "V9", "V10",
]


if __name__ == "__main__":
    from src.data.loader import load_raw
    from src.data.labeling import generate_labels

    df = load_raw()
    df = generate_labels(df)
    df = run_pipeline(df)
    print(df[FEATURE_COLS].head())
    print(f"\nFeatures ready: {len(FEATURE_COLS)}")