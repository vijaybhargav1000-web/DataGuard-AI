

\# DataGuard-AI



An end-to-end data engineering and AI-powered incident investigation platform built using Python, DuckDB, dbt, Apache Airflow, and a locally hosted LLM.



\## Project Overview



DataGuard-AI simulates a transaction data pipeline that detects data quality issues, quarantines invalid records, performs business analytics, and investigates data incidents using AI-assisted explanations.



The platform also supports human-in-the-loop remediation approval and audit logging.



\## Architecture



```text

Synthetic Transaction Producer

&#x20;             |

&#x20;             v

&#x20;      Raw JSONL Data

&#x20;             |

&#x20;             v

&#x20;   Data Quality Validation

&#x20;             |

&#x20;      +------+------+

&#x20;      |             |

&#x20;      v             v

&#x20;  Valid Data    Quarantined Data

&#x20;      |             |

&#x20;      v             v

&#x20;   DuckDB       Incident Agent

&#x20;      |             |

&#x20;      v             v

&#x20;   dbt Models   Evidence Validation

&#x20;      |             |

&#x20;      v             v

&#x20;Business Marts  Local LLM Explanation

&#x20;                    |

&#x20;                    v

&#x20;              Incident Report

&#x20;                    |

&#x20;                    v

&#x20;             Human Approval

&#x20;                    |

&#x20;                    v

&#x20;                Audit Log

```



\## Technology Stack



\- Python

\- Pandas

\- DuckDB

\- dbt-duckdb

\- Apache Airflow

\- Docker Compose

\- Ollama

\- Qwen 2.5 1.5B

\- Pytest

\- Git and GitHub



\## Implementation Stages



\### Stage 1 â€“ Data Ingestion and Quality Validation



\- Generated 1,000 synthetic transaction records.

\- Introduced 50 intentional data quality defects.

\- Validated transaction records.

\- Identified duplicate IDs, missing customer IDs, negative amounts, missing amounts, and unexpected schema columns.

\- Separated valid records from quarantined records.



\*\*Validation result:\*\* 950 valid records and 50 quarantined records.



\### Stage 2 â€“ Data Warehouse and Analytics



\- Loaded validated transactions into DuckDB.

\- Created dbt staging and analytical models.

\- Built business analytics marts.

\- Executed dbt tests to validate the models.



\*\*Validation result:\*\* 3 dbt models and 6 dbt tests passed.



\### Stage 3 â€“ Airflow Orchestration



Created an Airflow DAG to orchestrate the end-to-end data pipeline.



Tasks:



1\. Generate transactions.

2\. Validate transactions.

3\. Load data into DuckDB.

4\. Execute dbt models.

5\. Execute dbt tests.



\*\*Validation result:\*\* All 5 DAG tasks succeeded.



\### Stage 4 â€“ AI Incident Investigation and Remediation



Implemented a local AI-assisted incident investigation workflow.



Features:



\- Incident classification using Python orchestration.

\- Retrieval of quarantined transaction evidence.

\- Evidence validation before report generation.

\- Local LLM-powered incident explanations using Ollama and Qwen 2.5 1.5B.

\- Structured incident reports.

\- Human-in-the-loop remediation proposals.

\- Approval, rejection, and cancellation handling.

\- JSONL audit logging.



Supported incident types:



\- MISSING\_CUSTOMER\_ID

\- NEGATIVE\_AMOUNT

\- MISSING\_AMOUNT

\- UNEXPECTED\_SCHEMA\_COLUMNS

\- DUPLICATE\_TRANSACTION\_ID



The system does not automatically modify transaction data. Human approval authorizes the remediation plan only.



\## Project Structure



```text

DataGuard-AI/

|

|-- src/

|   |-- producer/

|   |-- validation/

|   |-- processing/

|   |-- agent/

|       |-- incident\_investigator.py

|       |-- report\_validator.py

|       |-- remediation\_workflow.py

|       |-- agent.py

|

|-- data/

|   |-- raw/

|   |-- processed/

|   |-- quarantine/

|

|-- dataguard\_analytics/

|   |-- models/

|

|-- airflow/

|   |-- dags/

|   |-- Dockerfile

|

|-- tests/

|   |-- test\_data\_quality\_engine.py

|   |-- test\_remediation\_workflow.py

|

|-- logs/

|-- pytest.ini

|-- README.md

|-- .gitignore

```



\## Local Setup



\### 1. Clone the repository



```bash

git clone https://github.com/vijaybhargav1000-web/DataGuard-AI.git

cd DataGuard-AI

```



\### 2. Create a Python virtual environment



```powershell

python -m venv .venv

.venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



Install the project dependencies used by the individual pipeline components, including:



\- pandas

\- duckdb

\- dbt-duckdb

\- pytest

\- requests



Airflow is configured separately through Docker Compose.



\### 4. Run automated tests



```powershell

pytest -v

```



\## Running the AI Incident Investigator



Install and start Ollama, then download the local model:



```powershell

ollama pull qwen2.5:1.5b

```



Start the Ollama service.



Run the investigator:



```powershell

python src/agent/agent.py

```



Example question:



```text

Investigate UNEXPECTED\_SCHEMA\_COLUMNS incidents

```



The system retrieves quarantined evidence, validates it, generates an AI explanation, and presents a remediation proposal.



The user can enter:



\- APPROVE

\- REJECT



Other inputs are recorded as CANCELLED.



All decisions are appended to:



```text

logs/remediation\_audit.jsonl

```



\## Testing



Run:



```powershell

pytest -v

```



The current automated test suite covers:



\- Transaction data quality validation.

\- Valid remediation proposal creation.

\- Blocking invalid evidence.

\- Blocking unsupported incident types.

\- Approval decision auditing.

\- Rejection decision auditing.

\- Invalid-input cancellation auditing.



\## Important Design Decisions



\- Python controls incident selection and evidence retrieval.

\- Evidence is validated before AI explanation generation.

\- The LLM explains verified evidence rather than determining factual counts.

\- Unknown root causes are explicitly reported as requiring further investigation.

\- Human approval is required before a remediation plan is authorized.

\- No automatic transaction corrections are performed.



\## Current Limitations



\- This is a local development and demonstration project, not a production deployment.

\- Ollama inference runs locally and depends on available hardware resources.

\- Remediation approval is a demonstration workflow without enterprise identity or role-based access control.

\- Approved remediation plans are not automatically executed.

\- The audit log is local JSONL storage rather than a centralized immutable audit system.

\- Root cause confirmation requires further investigation using source-system evidence.



\## Author



Vijay Bhargav



GitHub: https://github.com/vijaybhargav1000-web
