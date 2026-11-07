
import json
import uuid

from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

AUDIT_FILE = (
    PROJECT_ROOT
    / "logs"
    / "remediation_audit.jsonl"
)


REMEDIATION_ACTIONS = {
    "MISSING_CUSTOMER_ID": (
        "Investigate the source system and identify the correct "
        "customer IDs using an approved reference source."
    ),
    "NEGATIVE_AMOUNT": (
        "Verify the transaction amounts against the original "
        "source records and approved business rules."
    ),
    "MISSING_AMOUNT": (
        "Investigate why transaction amounts are missing and "
        "verify values against the source system."
    ),
    "UNEXPECTED_SCHEMA_COLUMNS": (
        "Review the unexpected columns and confirm whether the "
        "source schema change is legitimate."
    ),
    "DUPLICATE_TRANSACTION_ID": (
        "Investigate duplicate transaction IDs and verify the "
        "original transaction before deciding on corrections."
    ),
}


def create_remediation_proposal(result, validation):
    """Create a remediation proposal from validated evidence."""

    if not validation.get("valid"):
        raise ValueError(
            "Remediation proposal blocked: Evidence validation failed."
        )

    incident = result.get("incident")

    if incident not in REMEDIATION_ACTIONS:
        raise ValueError("Unsupported incident type.")

    return {
        "proposal_id": str(uuid.uuid4()),
        "incident": incident,
        "affected_records": result["affected_records"],
        "validated_records": validation["validated_records"],
        "validation_status": "PASSED",
        "proposed_action": REMEDIATION_ACTIONS[incident],
        "execution_status": "NOT_EXECUTED",
    }


def save_audit_record(record):
    """Append an approval decision to the audit log."""

    AUDIT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def run_remediation_workflow(result, validation):
    """Request human approval and record the decision."""

    proposal = create_remediation_proposal(
        result,
        validation,
    )

    print("\n========== REMEDIATION PROPOSAL ==========")

    print(f"Proposal ID: {proposal['proposal_id']}")
    print(f"Incident: {proposal['incident']}")
    print(f"Affected records: {proposal['affected_records']}")
    print(f"Validated records: {proposal['validated_records']}")

    print("\nProposed action:")
    print(proposal["proposed_action"])

    print("\nIMPORTANT:")
    print("Approval authorizes the remediation plan only.")
    print("No transaction data will be modified.")

    decision = input(
        "\nType APPROVE to approve or REJECT to reject: "
    ).strip().upper()

    if decision == "APPROVE":
        status = "APPROVED"

    elif decision == "REJECT":
        status = "REJECTED"

    else:
        status = "CANCELLED"

    audit_record = {
        **proposal,
        "decision": status,
        "decision_timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "execution_status": "NOT_EXECUTED",
    }

    save_audit_record(audit_record)

    print("\n========== REMEDIATION DECISION ==========")
    print(f"Decision: {status}")
    print("Execution status: NOT_EXECUTED")
    print(f"Audit log: {AUDIT_FILE}")

    return audit_record
