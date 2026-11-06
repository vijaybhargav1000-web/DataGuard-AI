import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

QUARANTINE_FILE = (
    PROJECT_ROOT
    / "data"
    / "quarantine"
    / "invalid_transactions.jsonl"
)


def investigate_incidents():
    issue_counts = Counter()

    with open(QUARANTINE_FILE, "r", encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)

            for issue in item["issues"]:
                issue_counts[issue] += 1

    return {
        "total_incidents": sum(issue_counts.values()),
        "incident_types": dict(issue_counts),
    }


def analyze_root_causes():
    root_causes = {
        "MISSING_CUSTOMER_ID": (
            "Customer ID is missing.",
            "Customer-level reporting may be affected.",
            "Validate customer_id before accepting transactions."
        ),
        "NEGATIVE_AMOUNT": (
            "Transaction amount contains a negative value.",
            "Financial calculations may become incorrect.",
            "Reject negative amounts during validation."
        ),
        "MISSING_AMOUNT": (
            "Transaction amount is missing.",
            "Transaction totals may be incomplete.",
            "Make amount mandatory during validation."
        ),
        "UNEXPECTED_SCHEMA_COLUMNS": (
            "Incoming transaction contains unexpected fields.",
            "Downstream schema compatibility may be affected.",
            "Review the new field and implement controlled schema evolution."
        ),
        "DUPLICATE_TRANSACTION_ID": (
            "Transaction ID already exists.",
            "Duplicate processing may affect transaction counts.",
            "Apply transaction ID-based deduplication."
        )
    }

    incidents = investigate_incidents()

    print(f"Total incidents: {incidents['total_incidents']}")

    for issue, count in incidents["incident_types"].items():
        cause, impact, recommendation = root_causes[issue]

        print(f"\nIncident: {issue}")
        print(f"Affected records: {count}")
        print(f"Root cause: {cause}")
        print(f"Business impact: {impact}")
        print(f"Recommendation: {recommendation}")


if __name__ == "__main__":
    analyze_root_causes()

def get_incident_evidence(issue_type):
    evidence = []

    with open(QUARANTINE_FILE, "r", encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)

            if issue_type in item["issues"]:
                evidence.append({
                    "transaction_id": item["record"].get("transaction_id"),
                    "source_line": item["source_line"],
                    "issues": item["issues"],
                    "record": item["record"]
                })

    return evidence

def investigate_incident(issue_type):
    valid_issues = investigate_incidents()["incident_types"]

    if issue_type not in valid_issues:
        return {"error": f"Unknown incident type: {issue_type}"}

    evidence = get_incident_evidence(issue_type)

    return {
        "incident": issue_type,
        "affected_records": len(evidence),
        "evidence": evidence[:3],
        "investigation_status": "COMPLETED"
    }