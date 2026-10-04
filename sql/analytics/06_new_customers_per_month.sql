-- Business question: How many new customers do we get each month, and how many in total so far?
WITH first_purchase AS (
    SELECT
        customer_id,
        date_trunc('month', MIN(invoiced_at))::date AS first_month
    FROM invoices
    WHERE customer_id IS NOT NULL
      AND invoice_no NOT LIKE 'C%'
    GROUP BY customer_id
)
SELECT
    first_month AS month,
    COUNT(*) AS new_customers,
    SUM(COUNT(*)) OVER (ORDER BY first_month) AS cumulative_customers
FROM first_purchase
GROUP BY first_month
ORDER BY first_month;