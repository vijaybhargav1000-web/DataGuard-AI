
import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = PROJECT_ROOT / "data/raw/transactions.jsonl"
VALID_FILE = PROJECT_ROOT / "data/processed/valid_transactions.jsonl"
QUARANTINE_FILE = (
    PROJECT_ROOT / "data/quarantine/invalid_transactions.jsonl"
)
REPORT_FILE = PROJECT_ROOT / "logs/data_quality_report.json"

EXPECTED_COLUMNS = {
    "transaction_id",
    "customer_id",
    "amount",
    "transaction_date",
    "transaction_type",
    "payment_status"
}


def load_transactions():
    """Load raw transactions from JSONL."""

    transactions = []

    with RAW_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                transactions.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Invalid JSON at line {line_number}")

    return transactions


def validate_transactions(transactions):
    """Validate records and separate valid and invalid transactions."""

    valid_records = []
    quarantine_records = []

    seen_transaction_ids = set()
    issue_counts = Counter()

    for line_number, record in enumerate(transactions, start=1):

        issues = []

        transaction_id = record.get("transaction_id")
        customer_id = record.get("customer_id")
        amount = record.get("amount")

        # 1. Check duplicate transaction IDs
        if not transaction_id:
            issues.append("MISSING_TRANSACTION_ID")
        elif transaction_id in seen_transaction_ids:
            issues.append("DUPLICATE_TRANSACTION_ID")
        else:
            seen_transaction_ids.add(transaction_id)

        # 2. Check missing customer IDs
        if not customer_id:
            issues.append("MISSING_CUSTOMER_ID")

        # 3. Check missing amounts
        if amount is None:
            issues.append("MISSING_AMOUNT")

        # 4. Check negative amounts
        elif isinstance(amount, (int, float)) and amount < 0:
            issues.append("NEGATIVE_AMOUNT")

        # 5. Check unexpected schema columns
        unexpected_columns = (
            set(record.keys()) - EXPECTED_COLUMNS
        )

        if unexpected_columns:
            issues.append(
                "UNEXPECTED_SCHEMA_COLUMNS"
            )

        if issues:
            issue_counts.update(issues)

            quarantine_records.append({
                "source_line": line_number,
                "issues": issues,
                "record": record
            })

        else:
            valid_records.append(record)

    report = {
        "total_records": len(transactions),
        "valid_records": len(valid_records),
        "invalid_records": len(quarantine_records),
        "issue_counts": dict(issue_counts)
    }

    return valid_records, quarantine_records, report


def save_jsonl(file_path, records):
    """Save records in JSON Lines format."""

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with file_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")


def save_report(report):
    """Save the data quality report."""

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)


def main():

    print("=" * 55)
    print("DATAGUARD AI - DATA QUALITY ENGINE")
    print("=" * 55)

    transactions = load_transactions()

    valid_records, quarantine_records, report = (
        validate_transactions(transactions)
    )

    save_jsonl(VALID_FILE, valid_records)
    save_jsonl(QUARANTINE_FILE, quarantine_records)
    save_report(report)

    print(f"Total records: {report['total_records']}")
    print(f"Valid records: {report['valid_records']}")
    print(f"Quarantined records: {report['invalid_records']}")

    print("\nDATA QUALITY ISSUES:")

    for issue, count in report["issue_counts"].items():
        print(f"{issue}: {count}")

    print("\nOUTPUT FILES:")
    print(f"Valid: {VALID_FILE}")
    print(f"Quarantine: {QUARANTINE_FILE}")
    print(f"Report: {REPORT_FILE}")

    print("=" * 55)
    print("DATA QUALITY PROCESSING COMPLETED")


if __name__ == "__main__":
    main()
