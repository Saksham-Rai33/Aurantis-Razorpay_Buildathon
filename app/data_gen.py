import random
import joblib

from src.data.loader import load_raw
from src.data.labeling import generate_labels
from src.features.engineer import run_pipeline, FEATURE_COLS

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Rohan", "Ananya", "Diya", "Saanvi", "Aadhya", "Kiara", "Myra",
    "Priya", "Neha", "Riya", "Anika",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Iyer", "Nair", "Reddy", "Rao", "Patel",
    "Mehta", "Joshi", "Kapoor", "Singh", "Das", "Chatterjee", "Menon",
]
PRODUCTS = [
    "Wireless Earbuds", "Running Shoes", "Smart Watch", "Backpack", "Sunglasses",
    "Bluetooth Speaker", "Yoga Mat", "Kitchen Blender", "Office Chair", "Desk Lamp",
    "Phone Case", "Laptop Sleeve", "Perfume", "Sneakers", "Wallet",
]
CITIES = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Pune", "Chennai",
    "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
]

MODEL_PATH = "results/model.pkl"


def _fake_customer(rng):
    name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
    phone = f"9{rng.randint(100000000, 999999999)}"
    address = f"{rng.randint(1, 999)}, {rng.choice(CITIES)}"
    email = f"{name.lower().replace(' ', '.')}.{rng.randint(100, 999)}@example.com"
    return name, phone, address, email


def generate_demo_orders(n=50, seed=42):
    rng = random.Random(seed)

    df = load_raw()
    df = generate_labels(df)
    df = run_pipeline(df)

    sample = df.sample(n=n, random_state=seed).reset_index(drop=True)
    X = sample[FEATURE_COLS].fillna(-999)

    model = joblib.load(MODEL_PATH)
    scores = model.predict_proba(X)[:, 1]

    orders = []
    for i, row in sample.iterrows():
        name, phone, address, email = _fake_customer(rng)
        feature_values = {col: float(row[col]) if row[col] == row[col] else -999.0 for col in FEATURE_COLS}
        orders.append({
            "order_id": int(row["TransactionID"]),
            "customer_name": name,
            "phone": phone,
            "email": email,
            "product_name": rng.choice(PRODUCTS),
            "address": address,
            "amount": float(row["TransactionAmt"]),
            "risk_score": float(scores[i]),
            **feature_values,
            "otp_code": None,
            "otp_provider": None,
            "otp_sent_at": None,
            "otp_verified": False,
            "otp_verified_at": None,
            "esign_sent_at": None,
            "esign_signed": False,
            "esign_signer": None,
            "esign_signed_at": None,
            "delivered": False,
            "delivered_at": None,
        })

    return orders


if __name__ == "__main__":
    demo_orders = generate_demo_orders(n=5)
    for o in demo_orders:
        print(o["order_id"], o["customer_name"], round(o["risk_score"], 3))
