
def validate_investigation_result(result):
    """
    Validate every retrieved evidence record against its incident type.
    """

    errors = []
    warnings = []

    if result.get("investigation_status") != "COMPLETED":
        errors.append("Investigation is not completed.")

    if not result.get("evidence_validation", {}).get(
        "confirmed_from_quarantine"
    ):
        errors.append("Evidence source is not verified.")

    incident = result.get("incident")

    affected_records = result.get("affected_records")
    total_evidence = result.get("total_evidence_records")
    evidence = result.get("sample_evidence", [])

    if not isinstance(affected_records, int) or isinstance(
        affected_records, bool
    ) or affected_records < 0:
        errors.append("Invalid affected record count.")

    if not isinstance(total_evidence, int) or isinstance(
        total_evidence, bool
    ) or total_evidence < 0:
        errors.append("Invalid total evidence count.")

    if isinstance(affected_records, int) and isinstance(
        total_evidence, int
    ):
        if affected_records != total_evidence:
            errors.append("Affected record count mismatch.")

    if not isinstance(evidence, list):
        errors.append("Evidence must be a list.")
        evidence = []

    if len(evidence) != total_evidence:
        errors.append(
            "Evidence record count does not match total evidence count."
        )

    supported_incidents = {
        "MISSING_CUSTOMER_ID",
        "NEGATIVE_AMOUNT",
        "MISSING_AMOUNT",
        "UNEXPECTED_SCHEMA_COLUMNS",
        "DUPLICATE_TRANSACTION_ID",
    }

    if incident not in supported_incidents:
        errors.append("Unsupported incident type.")

    seen_transaction_ids = set()

    for index, item in enumerate(evidence, start=1):

        if not isinstance(item, dict):
            errors.append(f"Evidence record {index} is invalid.")
            continue

        transaction = item.get("record", {})

        if not isinstance(transaction, dict):
            errors.append(
                f"Evidence record {index} has an invalid transaction."
            )
            continue

        transaction_id = transaction.get("transaction_id")

        if not transaction_id:
            errors.append(
                f"Evidence record {index} has no transaction ID."
            )
        elif transaction_id in seen_transaction_ids:
            errors.append(
                f"Duplicate evidence transaction ID: {transaction_id}"
            )
        else:
            seen_transaction_ids.add(transaction_id)

        issues = item.get("issues", [])

        if incident not in issues:
            errors.append(
                f"Evidence record {index} does not match incident type."
            )

        if incident == "MISSING_CUSTOMER_ID":
            if transaction.get("customer_id") is not None:
                errors.append(
                    f"{transaction_id}: Customer ID is not missing."
                )

        elif incident == "NEGATIVE_AMOUNT":
            amount = transaction.get("amount")

            if not isinstance(amount, (int, float)) or isinstance(
                amount, bool
            ) or amount >= 0:
                errors.append(
                    f"{transaction_id}: Amount is not negative."
                )

        elif incident == "MISSING_AMOUNT":
            if transaction.get("amount") is not None:
                errors.append(
                    f"{transaction_id}: Amount is not missing."
                )

        elif incident == "UNEXPECTED_SCHEMA_COLUMNS":
            if not item.get("unexpected_fields"):
                errors.append(
                    f"{transaction_id}: Unexpected fields are not identified."
                )

        elif incident == "DUPLICATE_TRANSACTION_ID":
            if "DUPLICATE_TRANSACTION_ID" not in issues:
                errors.append(
                    f"{transaction_id}: Duplicate issue is not confirmed."
                )

    if result.get("root_cause_status") == (
        "REQUIRES_FURTHER_INVESTIGATION"
    ):
        warnings.append(
            "Exact root cause has not been established."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "total_evidence_records": total_evidence,
        "validated_records": len(evidence),
    }
