
import json
import requests

from incident_investigator import (
    investigate_incidents,
    investigate_incident,
)

from report_validator import validate_investigation_result

from remediation_workflow import run_remediation_workflow


MODEL = "qwen2.5:1.5b"
OLLAMA_URL = "http://localhost:11434/api/chat"


def generate_ai_explanation(incident, evidence_summary):
    """Generate a short explanation using verified facts."""

    prompt = f"""
You are a data engineering incident analyst.

Explain this incident in simple business English.

Incident: {incident}

Verified evidence:
{json.dumps(evidence_summary)}

Rules:
- Use only supplied facts.
- Never invent numbers, causes or financial losses.
- Do not claim fraud.
- Do not recommend automatic corrections.
- Keep your explanation under 80 words.
- If the root cause is unknown, say so.

Return only the explanation.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 120,
                "num_ctx": 2048,
            },
        },
        timeout=300,
    )

    response.raise_for_status()

    return response.json()["message"]["content"].strip()


def build_evidence_summary(result):
    """Build a compact summary from verified Python evidence."""

    evidence = result["sample_evidence"]
    incident = result["incident"]

    summary = {
        "incident": incident,
        "affected_records": result["affected_records"],
        "validated_records": len(evidence),
        "root_cause": "Not established",
        "evidence_validation": "PASSED",
    }

    if incident == "UNEXPECTED_SCHEMA_COLUMNS":
        summary["unexpected_fields"] = sorted({
            field
            for item in evidence
            for field in item.get("unexpected_fields", [])
        })

    elif incident == "NEGATIVE_AMOUNT":
        summary["negative_amount_records"] = len(evidence)

    elif incident == "MISSING_AMOUNT":
        summary["missing_amount_records"] = len(evidence)

    elif incident == "MISSING_CUSTOMER_ID":
        summary["missing_customer_id_records"] = len(evidence)

    elif incident == "DUPLICATE_TRANSACTION_ID":
        summary["duplicate_issue_records"] = len(evidence)

    return summary


def build_report(incident, summary, explanation, validation):
    """Generate factual report sections using Python."""

    lines = [
        "\n========== DATAGUARD AI INCIDENT REPORT ==========",
        "\n1. INCIDENT SUMMARY",
        f"Incident type: {incident}",
        f"Affected records: {summary['affected_records']}",
        "\n2. CONFIRMED EVIDENCE",
        f"Validated records: {validation['validated_records']}",
    ]

    if "unexpected_fields" in summary:
        lines.append(
            f"Unexpected fields: {', '.join(summary['unexpected_fields'])}"
        )

    lines.extend([
        "\n3. ROOT CAUSE ANALYSIS",
        "Exact root cause: Not established. Further investigation is required.",
        "\n4. BUSINESS-FRIENDLY EXPLANATION",
        explanation,
        "\n5. RECOMMENDED REMEDIATION",
        "Investigate the source data and identify the cause.",
        "Prepare a correction plan and obtain human approval before applying changes.",
        "\n6. EVIDENCE GAPS",
        "The originating cause has not yet been confirmed.",
        "\n7. EVIDENCE VALIDATION",
        f"Validation status: {'PASSED' if validation['valid'] else 'FAILED'}",
        f"Records validated: {validation['validated_records']}",
        f"Validation errors: {len(validation['errors'])}",
        "\n===================================================",
    ])

    return "\n".join(lines)


def run_agent(question):

    summary = investigate_incidents()

    issue_types = [
        "MISSING_CUSTOMER_ID",
        "NEGATIVE_AMOUNT",
        "MISSING_AMOUNT",
        "UNEXPECTED_SCHEMA_COLUMNS",
        "DUPLICATE_TRANSACTION_ID",
    ]

    selected_issue = next(
        (
            issue
            for issue in issue_types
            if issue.lower() in question.lower()
        ),
        None,
    )

    if not selected_issue:
        return (
            "Please specify one supported incident type:\n"
            + "\n".join(issue_types)
        )

    print(f"\nPython selected incident: {selected_issue}")

    result = investigate_incident(selected_issue)

    if "error" in result:
        return json.dumps(result, indent=2)

    validation = validate_investigation_result(result)

    print("\n========== PYTHON VALIDATION ==========")
    print(json.dumps(validation, indent=2))

    if not validation["valid"]:
        return (
            "Investigation blocked: Evidence validation failed.\n"
            + json.dumps(validation, indent=2)
        )

    evidence_summary = build_evidence_summary(result)

    print("\nEvidence validated. Generating AI explanation...")

    try:
        explanation = generate_ai_explanation(
            selected_issue,
            evidence_summary,
        )

    except requests.RequestException as error:
        print(f"\nOllama unavailable: {error}")

        explanation = (
            "AI explanation is unavailable. "
            "The verified Python investigation results are still available."
        )

    report = build_report(
        selected_issue,
        evidence_summary,
        explanation,
        validation,
    )

    print(report)

    # Human-in-the-loop remediation workflow
    approval_result = run_remediation_workflow(
        result,
        validation,
    )

    return (
        "\n========== FINAL WORKFLOW STATUS ==========\n"
        f"Incident: {selected_issue}\n"
        f"Human decision: {approval_result['decision']}\n"
        f"Execution status: {approval_result['execution_status']}\n"
        "No transaction data was modified."
    )


if __name__ == "__main__":

    print("\n========== DATAGUARD AI ==========")

    question = input("\nWhat would you like me to investigate? ")

    print("\nAgent is investigating...\n")

    try:
        final_status = run_agent(question)
        print(final_status)

    except requests.RequestException as error:
        print(f"Ollama connection error: {error}")

    except Exception as error:
        print(f"Agent error: {error}")
