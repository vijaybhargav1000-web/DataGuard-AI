{{ config(materialized='table') }}

SELECT
    payment_status,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS average_amount

FROM {{ ref('stg_transactions') }}

GROUP BY payment_status