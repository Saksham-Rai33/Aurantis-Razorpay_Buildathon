import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

from src.features.engineer import FEATURE_COLS

RANDOM_SEED = 42
TARGET = "return_risk"


def split_data(df):
    X = df[FEATURE_COLS].fillna(-999)
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        stratify=y,
        random_state=RANDOM_SEED
    )

    print(f"Train: {len(X_train):,} rows | Positives: {y_train.sum():,} ({y_train.mean():.2%})")
    print(f"Test:  {len(X_test):,} rows  | Positives: {y_test.sum():,} ({y_test.mean():.2%})")

    return X_train, X_test, y_train, y_test


def apply_smote(X_train, y_train):
    print("Applying SMOTE...")
    print(f"Before: {y_train.value_counts().to_dict()}")

    smote = SMOTE(sampling_strategy=0.2, random_state=RANDOM_SEED)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    print(f"After:  {pd.Series(y_resampled).value_counts().to_dict()}")
    return X_resampled, y_resampled


if __name__ == "__main__":
    from src.data.loader import load_raw
    from src.data.labeling import generate_labels
    from src.features.engineer import run_pipeline

    df = load_raw()
    df = generate_labels(df)
    df = run_pipeline(df)

    X_train, X_test, y_train, y_test = split_data(df)
    X_train_sm, y_train_sm = apply_smote(X_train, y_train)

    print(f"\nFinal training set size: {len(X_train_sm):,}")
    print(f"Final test set size: {len(X_test):,}")