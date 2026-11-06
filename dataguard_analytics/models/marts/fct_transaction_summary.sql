{{ config(materialized='table') }}

SELECT
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_transaction_amount,
    ROUND(AVG(amount), 2) AS average_transaction_amount,
    MIN(amount) AS minimum_transaction_amount,
    MAX(amount) AS maximum_transaction_amount

FROM {{ ref('stg_transactions') }}