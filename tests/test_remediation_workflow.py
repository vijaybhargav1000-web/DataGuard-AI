
import json

import pytest

from src.agent import remediation_workflow as workflow


@pytest.fixture
def valid_result():
    return {
        "incident": "MISSING_AMOUNT",
        "affected_records": 2,
    }


@pytest.fixture
def valid_validation():
    return {
        "valid": True,
        "validated_records": 2,
        "errors": [],
    }


def test_create_valid_remediation_proposal(
    valid_result,
    valid_validation,
):
    proposal = workflow.create_remediation_proposal(
        valid_result,
        valid_validation,
    )

    assert proposal["incident"] == "MISSING_AMOUNT"
    assert proposal["affected_records"] == 2
    assert proposal["validated_records"] == 2
    assert proposal["validation_status"] == "PASSED"
    assert proposal["execution_status"] == "NOT_EXECUTED"


def test_invalid_evidence_blocks_proposal(valid_result):
    invalid_validation = {
        "valid": False,
        "validated_records": 0,
        "errors": ["Evidence validation failed"],
    }

    with pytest.raises(ValueError):
        workflow.create_remediation_proposal(
            valid_result,
            invalid_validation,
        )


def test_unsupported_incident_blocks_proposal(
    valid_validation,
):
    invalid_result = {
        "incident": "UNKNOWN_INCIDENT",
        "affected_records": 1,
    }

    with pytest.raises(ValueError):
        workflow.create_remediation_proposal(
            invalid_result,
            valid_validation,
        )


@pytest.mark.parametrize(
    ("user_input", "expected_decision"),
    [
        ("APPROVE", "APPROVED"),
        ("REJECT", "REJECTED"),
        ("INVALID", "CANCELLED"),
    ],
)
def test_remediation_decisions_are_audited(
    monkeypatch,
    tmp_path,
    valid_result,
    valid_validation,
    user_input,
    expected_decision,
):
    audit_file = tmp_path / "remediation_audit.jsonl"

    monkeypatch.setattr(
        workflow,
        "AUDIT_FILE",
        audit_file,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: user_input,
    )

    result = workflow.run_remediation_workflow(
        valid_result,
        valid_validation,
    )

    assert result["decision"] == expected_decision
    assert result["execution_status"] == "NOT_EXECUTED"

    audit_records = [
        json.loads(line)
        for line in audit_file.read_text(
            encoding="utf-8"
        ).splitlines()
    ]

    assert len(audit_records) == 1
    assert audit_records[0]["decision"] == expected_decision
    assert audit_records[0]["execution_status"] == "NOT_EXECUTED"
