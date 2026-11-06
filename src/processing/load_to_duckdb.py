import json
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data/processed/valid_transactions.jsonl"
DATABASE_FILE = PROJECT_ROOT / "data/processed/dataguard.duckdb"


def load_transactions():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    transactions = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            transactions.append(json.loads(line))

    return transactions


def create_database(transactions):

    con = duckdb.connect(str(DATABASE_FILE))

    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id VARCHAR PRIMARY KEY,
                customer_id VARCHAR,
                amount DOUBLE,
                transaction_date TIMESTAMP WITH TIME ZONE,
                transaction_type VARCHAR,
                payment_status VARCHAR
            )
        """)

        con.executemany("""
            INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (transaction_id) DO NOTHING
        """, [
            (
                record["transaction_id"],
                record["customer_id"],
                record["amount"],
                record["transaction_date"],
                record["transaction_type"],
                record["payment_status"]
            )
            for record in transactions
        ])

        total_records = con.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]

        return total_records

    finally:
        con.close()


def main():

    print("\nDATAGUARD AI - DUCKDB LOADER")

    transactions = load_transactions()

    total_records = create_database(transactions)

    print(f"Input records: {len(transactions)}")
    print(f"Database records: {total_records}")
    print(f"Database location: {DATABASE_FILE}")

    print("\nDUCKDB LOADING COMPLETED")


if __name__ == "__main__":
    main()