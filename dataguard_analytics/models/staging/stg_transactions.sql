{{ config(materialized='view') }}

SELECT
    transaction_id,
    customer_id,
    amount,
    transaction_date,
    transaction_type,
    payment_status

FROM transactions

WHERE transaction_id IS NOT NULL
  AND customer_id IS NOT NULL
  AND amount IS NOT NULL
  AND amount >= 0