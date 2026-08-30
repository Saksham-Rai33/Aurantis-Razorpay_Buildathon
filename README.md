# Return-Risk Scorer — Razorpay AI Buildathon 2026

> **Track 2 — AI Risk Manager**  
> Predicts return-abuse probability at checkout so merchants can intervene before a loss occurs.

## Problem

Return abuse costs Indian e-commerce merchants thousands of crores annually. Unlike fraud, the transaction itself looks completely legitimate — the abuse happens after the sale. Merchants currently have no real-time signal at checkout that tells them this order is likely to become a return abuse event.

## Solution

A LightGBM classifier that scores every order at checkout (0–1) based on behavioral, transactional, and identity signals. Merchants use this score to decide whether to ship normally, require a signature, or flag for review.

## Dataset

- Source: IEEE-CIS Fraud Detection (Kaggle) — 590,540 transactions
- Labels: Synthetic return-risk labels generated via domain-driven scoring (see `src/data/labeling.py`)
- Positive rate: 5.89% (realistic for return abuse in Indian e-commerce)

## Model Performance

> To be filled after training (Day 2)

| Metric | Score |
|--------|-------|
| ROC-AUC | — |
| PR-AUC | — |
| Precision | — |
| Recall | — |

## How to Run

```bash
pip install -r requirements.txt
python -m src.data.labeling
```

## Build Log

| Day | Date | What shipped |
|-----|------|-------------|
| 0 | Aug 30 | Scaffold, data loader, labeling function, README |

## Author

Yatharth | B.Tech CSE (Data Science), Navrachana University  
Razorpay AI Buildathon 2026 — Track 2: AI Risk Manager