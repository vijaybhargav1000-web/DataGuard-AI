# DataGuard-AI

An end-to-end data engineering and AI-powered incident investigation platform built using Python, DuckDB, dbt, Apache Airflow, and a locally hosted LLM.

## Project Overview

DataGuard-AI simulates a transaction data pipeline that detects data quality issues, quarantines invalid records, performs business analytics, and investigates data incidents using AI-assisted explanations.

The platform also supports human-in-the-loop remediation approval and audit logging.

## Architecture

```text
Synthetic Transaction Producer
              |
              v
       Raw JSONL Data
              |
              v
    Data Quality Validation
              |
       +------+------+
       |             |
       v             v
   Valid Data    Quarantined Data
       |             |
       v             v
    DuckDB       Incident Agent
       |             |
       v             v
    dbt Models   Evidence Validation
       |             |
       v             v
 Business Marts  Local LLM Explanation
                     |
                     v
               Incident Report
                     |
                     v
              Human Approval
                     |
                     v
                  Audit Log
```

## Technology Stack

- Python
- Pandas
- DuckDB
- dbt-duckdb
- Apache Airflow
- Docker Compose
- Ollama
- Qwen 2.5 1.5B
- Pytest
- Git and GitHub

## Implementation Stages

### Stage 1 – Data Ingestion and Quality Validation

- Generated 1,000 synthetic transaction records.
- Introduced 50 intentional data quality defects.
- Validated transaction records.
- Identified duplicate IDs, missing customer IDs, negative amounts, missing amounts, and unexpected schema columns.
- Separated valid records from quarantined records.

**Validation result:** 950 valid records and 50 quarantined records.

### Stage 2 – Data Warehouse and Analytics

- Loaded validated transactions into DuckDB.
- Created dbt staging and analytical models.
- Built business analytics marts.
- Executed dbt tests to validate the models.

**Validation result:** 3 dbt models and 6 dbt tests passed.

### Stage 3 – Airflow Orchestration

Created an Airflow DAG to orchestrate the end-to-end data pipeline.

Tasks:

1. Generate transactions.
2. Validate transactions.
3. Load data into DuckDB.
4. Execute dbt models.
5. Execute dbt tests.

**Validation result:** All 5 DAG tasks succeeded.

### Stage 4 – AI Incident Investigation and Remediation

Implemented a local AI-assisted incident investigation workflow.

Features:

- Incident classification using Python orchestration.
- Retrieval of quarantined transaction evidence.
- Evidence validation before report generation.
- Local LLM-powered incident explanations using Ollama and Qwen 2.5 1.5B.
- Structured incident reports.
- Human-in-the-loop remediation proposals.
- Approval, rejection, and cancellation handling.
- JSONL audit logging.

Supported incident types:

- `MISSING_CUSTOMER_ID`
- `NEGATIVE_AMOUNT`
- `MISSING_AMOUNT`
- `UNEXPECTED_SCHEMA_COLUMNS`
- `DUPLICATE_TRANSACTION