
import json
import requests

from incident_investigator import (
    investigate_incidents,
    get_incident_evidence,
)

MODEL = "qwen2.5:1.5b"
OLLAMA_URL = "http://localhost:11434/api/chat"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_incident_summary",
            "description": "Get counts of all quarantined incident types.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_incident_evidence",
            "description": "Retrieve actual quarantined transaction records for an incident type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "enum": [
                            "MISSING_CUSTOMER_ID",
                            "NEGATIVE_AMOUNT",
                            "MISSING_AMOUNT",
                            "UNEXPECTED_SCHEMA_COLUMNS",
                            "DUPLICATE_TRANSACTION_ID",
                        ],
                    }
                },
                "required": ["issue_type"],
            },
        },
    },
]


SYSTEM_PROMPT = """
You are DataGuard AI, a production data quality incident investigator.

Your responsibility is to investigate incidents using the available
Python tools.

STRICT INVESTIGATION RULES:

1. Always use the available tools to retrieve actual incident evidence.
2. Treat tool output as the only source of factual evidence.
3. Never invent transaction IDs, customer IDs, amounts, or incident counts.
4. Clearly distinguish:
   - Observed facts: Directly available in retrieved records.
   - Possible root causes: Hypotheses requiring further investigation.
   - Potential business impact: Risks, not confirmed losses.
5. Never claim financial loss, customer churn, or incorrect charges
   unless retrieved evidence explicitly proves it.
6. If the exact root cause is unknown, explicitly state:
   "The exact root cause cannot be confirmed from the available evidence."
7. Never automatically generate or assign missing customer IDs.
8. Never modify, delete, or update transaction records.
9. Recommend quarantine, validation, reconciliation, and human approval
   wherever appropriate.
10. Never describe a recommended action as already completed.

RESPONSE FORMAT:

1. Incident Summary
2. Actual Evidence
3. Root Cause Analysis
4. Potential Business Impact
5. Recommended Remediation
6. Evidence Gaps

Keep the response concise and professional.
Do not present assumptions as confirmed facts.
"""


def execute_tool(name, arguments):

    if name == "get_incident_summary":
        return investigate_incidents()

    if name == "get_incident_evidence":

        issue_type = arguments.get("issue_type")

        allowed_issues = investigate_incidents()["incident_types"]

        if issue_type not in allowed_issues:
            return {"error": "Invalid incident type"}

        evidence = get_incident_evidence(issue_type)

        return {
            "incident": issue_type,
            "affected_records": len(evidence),
            "sample_evidence": evidence[:3],
        }

    return {"error": f"Unknown tool: {name}"}


def run_agent(question):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    for step in range(5):

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "tools": TOOLS,
                "stream": False,
            },
            timeout=180,
        )

        response.raise_for_status()

        assistant_message = response.json()["message"]

        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls", [])

        if not tool_calls:
            return assistant_message.get("content", "")

        for tool_call in tool_calls:

            function = tool_call["function"]

            tool_name = function["name"]

            arguments = function.get("arguments", {})

            print(f"\nAgent selected tool: {tool_name}")
            print(f"Arguments: {arguments}")

            result = execute_tool(tool_name, arguments)

            messages.append({
                "role": "tool",
                "content": json.dumps(result),
            })

    return "Investigation stopped after reaching the tool-call limit."


if __name__ == "__main__":

    print("\n========== DATAGUARD AI ==========")

    question = input("\nWhat would you like me to investigate? ")

    print("\nAgent is investigating...\n")

    try:

        result = run_agent(question)

        print("\n========== INVESTIGATION REPORT ==========")

        print(result)

    except requests.RequestException as error:

        print(f"Ollama connection error: {error}")

    except Exception as error:

        print(f"Agent error: {error}")
