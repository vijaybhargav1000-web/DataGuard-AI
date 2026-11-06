from pathlib import Path
import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_FILE = PROJECT_ROOT / "data/processed/dataguard.duckdb"


def main():

    con = duckdb.connect(str(DATABASE_FILE), read_only=True)

    print("\nDATAGUARD AI - BUSINESS ANALYTICS")

    print("\n1. TRANSACTION SUMMARY")

    summary = con.execute("""
        SELECT
            COUNT(*) AS total_transactions,
            ROUND(SUM(amount), 2) AS total_amount,
            ROUND(AVG(amount), 2) AS average_amount,
            MAX(amount) AS maximum_amount
        FROM transactions
    """).fetchone()

    print("Total transactions:", summary[0])
    print("Total amount:", summary[1])
    print("Average amount:", summary[2])
    print("Maximum amount:", summary[3])

    print("\n2. PAYMENT STATUS SUMMARY")

    statuses = con.execute("""
        SELECT payment_status, COUNT(*)
        FROM transactions
        GROUP BY payment_status
        ORDER BY payment_status
    """).fetchall()

    for status, count in statuses:
        print(status, ":", count)

    print("\n3. TRANSACTION TYPE SUMMARY")

    types = con.execute("""
        SELECT transaction_type, COUNT(*)
        FROM transactions
        GROUP BY transaction_type
        ORDER BY transaction_type
    """).fetchall()

    for transaction_type, count in types:
        print(transaction_type, ":", count)

    con.close()


if __name__ == "__main__":
    main()