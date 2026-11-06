
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


# Project configuration
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_FILE = PROJECT_ROOT / "data" / "raw" / "transactions.jsonl"

TOTAL_TRANSACTIONS = 1000
RANDOM_SEED = 42

random.seed(RANDOM_SEED)


def generate_transaction(transaction_number):
    """Generate one realistic financial transaction."""

    return {
        "transaction_id": f"TXN{transaction_number:06d}",
        "customer_id": f"CUST{random.randint(1000, 9999)}",
        "amount": round(random.uniform(100, 50000), 2),
        "transaction_date": (
            datetime.now(timezone.utc)
            - timedelta(days=random.randint(0, 30))
        ).isoformat(),
        "transaction_type": random.choice(
            ["UPI", "CARD", "BANK_TRANSFER"]
        ),
        "payment_status": random.choice(
            ["SUCCESS", "FAILED", "PENDING"]
        )
    }


def introduce_data_quality_issues(transactions):
    """Simulate common production data-quality problems."""

    # 1. Introduce duplicate transaction IDs
    for index in range(10):
        transactions[990 + index]["transaction_id"] = (
            transactions[index]["transaction_id"]
        )

    # 2. Introduce missing customer IDs
    for index in range(10, 20):
        transactions[index]["customer_id"] = None

    # 3. Introduce negative transaction amounts
    for index in range(20, 30):
        transactions[index]["amount"] = -500.00

    # 4. Introduce missing transaction amounts
    for index in range(30, 40):
        transactions[index]["amount"] = None

    # 5. Introduce unexpected schema fields
    for index in range(40, 50):
        transactions[index]["merchant_region"] = "SOUTH"

    return transactions


def save_transactions(transactions):
    """Save transactions in JSON Lines format."""

    RAW_DATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with RAW_DATA_FILE.open("w", encoding="utf-8") as file:
        for transaction in transactions:
            file.write(json.dumps(transaction) + "\n")


def main():

    print("=" * 50)
    print("DATAGUARD AI - TRANSACTION PRODUCER")
    print("=" * 50)

    transactions = [
        generate_transaction(index + 1)
        for index in range(TOTAL_TRANSACTIONS)
    ]

    transactions = introduce_data_quality_issues(
        transactions
    )

    save_transactions(transactions)

    print(f"Total transactions generated: {len(transactions)}")
    print("Duplicate IDs introduced: 10")
    print("Missing customer IDs introduced: 10")
    print("Negative amounts introduced: 10")
    print("Missing amounts introduced: 10")
    print("Unexpected schema fields introduced: 10")
    print(f"Output file: {RAW_DATA_FILE}")

    print("=" * 50)
    print("TRANSACTION GENERATION COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()
