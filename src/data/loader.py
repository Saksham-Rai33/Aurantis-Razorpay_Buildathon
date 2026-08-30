import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

def load_raw():
    print("Loading transactions...")
    txn = pd.read_csv(RAW_DIR / "train_transaction.csv")
    
    print("Loading identity...")
    identity = pd.read_csv(RAW_DIR / "train_identity.csv")
    
    print("Merging...")
    df = txn.merge(identity, on="TransactionID", how="left")
    
    print(f"Done. Shape: {df.shape}")
    return df

if __name__ == "__main__":
    df = load_raw()
    print(df.head())