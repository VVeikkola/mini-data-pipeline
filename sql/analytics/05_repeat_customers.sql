-- Business question: How many customers buy more than once?
-- Invoices without a customer (unknown customers) cannot be attributed and are excluded.
WITH orders_per_customer AS (
    SELECT
        customer_id,
        COUNT(*) AS orders
    FROM invoices
    WHERE customer_id IS NOT NULL
      AND invoice_no NOT LIKE 'C%'
      AND invoice_no NOT LIKE 'A%'
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS customers,
    COUNT(*) FILTER (WHERE orders > 1) AS repeat_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE orders > 1) / COUNT(*), 1) AS repeat_rate_pct,
    ROUND(AVG(orders), 1) AS avg_orders_per_customer,
    MAX(orders) AS max_orders
FROM orders_per_customer;