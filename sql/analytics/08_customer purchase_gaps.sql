-- Business question: How long do repeat customers typically wait between orders?
WITH customer_orders AS (
    SELECT
        customer_id,
        invoiced_at,
        LAG(invoiced_at) OVER (PARTITION BY customer_id ORDER BY invoiced_at) AS previous_order_at
    FROM invoices
    WHERE customer_id IS NOT NULL
      AND invoice_no NOT LIKE 'C%'
      AND invoice_no NOT LIKE 'A%'
),
gaps AS (
    SELECT invoiced_at::date - previous_order_at::date AS days_between
    FROM customer_orders
    WHERE previous_order_at IS NOT NULL
)
SELECT
    COUNT(*) AS repeat_orders,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY days_between) AS median_days,
    ROUND(AVG(days_between), 1) AS avg_days,
    COUNT(*) FILTER (WHERE days_between = 0) AS same_day_orders
FROM gaps;