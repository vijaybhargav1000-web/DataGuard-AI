
from src.validation.data_quality_engine import validate_transactions


def valid_transaction():
    return {
        "transaction_id": "TXN001",
        "customer_id": "CUST1001",
        "amount": 1500.00,
        "transaction_date": "2026-11-06T10:00:00+00:00",
        "transaction_type": "UPI",
        "payment_status": "SUCCESS"
    }


def test_valid_transaction():
    valid, quarantine, report = validate_transactions(
        [valid_transaction()]
    )

    assert len(valid) == 1
    assert len(quarantine) == 0


def test_duplicate_transaction():
    transaction1 = valid_transaction()
    transaction2 = valid_transaction()

    valid, quarantine, report = validate_transactions(
        [transaction1, transaction2]
    )

    assert len(valid) == 1
    assert len(quarantine) == 1
    assert "DUPLICATE_TRANSACTION_ID" in quarantine[0]["issues"]


def test_missing_customer_id():
    transaction = valid_transaction()
    transaction["customer_id"] = None

    valid, quarantine, report = validate_transactions(
        [transaction]
    )

    assert len(valid) == 0
    assert "MISSING_CUSTOMER_ID" in quarantine[0]["issues"]


def test_negative_amount():
    transaction = valid_transaction()
    transaction["amount"] = -500

    valid, quarantine, report = validate_transactions(
        [transaction]
    )

    assert len(valid) == 0
    assert "NEGATIVE_AMOUNT" in quarantine[0]["issues"]


def test_missing_amount():
    transaction = valid_transaction()
    transaction["amount"] = None

    valid, quarantine, report = validate_transactions(
        [transaction]
    )

    assert len(valid) == 0
    assert "MISSING_AMOUNT" in quarantine[0]["issues"]


def test_unexpected_schema_column():
    transaction = valid_transaction()
    transaction["unexpected_field"] = "UNKNOWN"

    valid, quarantine, report = validate_transactions(
        [transaction]
    )

    assert len(valid) == 0
    assert "UNEXPECTED_SCHEMA_COLUMNS" in quarantine[0]["issues"]
