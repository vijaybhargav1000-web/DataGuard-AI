
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

EXPECTED_COLUMNS = {
    "transaction_id",
    "customer_id",
    "amount",
    "transaction_date",
    "transaction_type",
    "payment_status",
}


def load_quarantine_records():
    """Load all quarantined transaction records."""

    records = []

    if not QUARANTINE_FILE.exists():
        raise FileNotFoundError(
            f"Quarantine file not found: {QUARANTINE_FILE}"
        )

    with open(QUARANTINE_FILE, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON at line {line_number}: {error}"
                ) from error

    return records


def investigate_incidents():
    """Return exact incident counts."""

    records = load_quarantine_records()

    issue_counts = Counter()
    affected_records = Counter()

    for item in records:
        issues = item.get("issues", [])

        for issue in set(issues):
            affected_records[issue] += 1

        for issue in issues:
            issue_counts[issue] += 1

    return {
        "total_quarantined_records": len(records),
        "total_incident_occurrences": sum(issue_counts.values()),
        "incident_types": dict(issue_counts),
        "affected_records_by_type": dict(affected_records),
    }


def get_incident_evidence(issue_type):
    """Retrieve all actual evidence for an incident."""

    records = load_quarantine_records()
    evidence = []

    for item in records:

        if issue_type not in item.get("issues", []):
            continue

        transaction = item.get("record", {})

        unexpected_fields = sorted(
            set(transaction.keys()) - EXPECTED_COLUMNS
        )

        evidence.append({
            "transaction_id": transaction.get("transaction_id"),
            "source_line": item.get("source_line"),
            "issues": item.get("issues", []),
            "record": transaction,
            "unexpected_fields": unexpected_fields,
        })

    return evidence


def investigate_incident(issue_type):
    """Perform deterministic incident investigation."""

    incident_summary = investigate_incidents()

    if issue_type not in incident_summary["incident_types"]:
        return {
            "error": f"Unknown incident type: {issue_type}"
        }

    evidence = get_incident_evidence(issue_type)

    return {
        "incident": issue_type,
        "affected_records": len(evidence),
        "total_evidence_records": len(evidence),
        "sample_evidence": evidence,
        "evidence_validation": {
            "confirmed_from_quarantine": True,
            "evidence_source": str(QUARANTINE_FILE),
        },
        "investigation_status": "COMPLETED",
        "root_cause_status": "REQUIRES_FURTHER_INVESTIGATION",
    }


def analyze_root_causes():
    """Display incident counts without claiming unverified causes."""

    incidents = investigate_incidents()

    print(
        f"Total quarantined records: "
        f"{incidents['total_quarantined_records']}"
    )

    print(
        f"Total incident occurrences: "
        f"{incidents['total_incident_occurrences']}"
    )

    for issue, count in incidents["incident_types"].items():

        print(f"\nIncident: {issue}")
        print(f"Affected records: {count}")
        print("Root cause: Requires further investigation.")
        print("Business impact: Potential downstream data quality risk.")


if __name__ == "__main__":
    analyze_root_causes()
