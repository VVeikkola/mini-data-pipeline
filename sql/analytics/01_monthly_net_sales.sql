-- Business question: How much did we sell each month, and how did it change from the previous month?
-- Net sales = sales minus cancellations. Fees, stock and accounting adjustments are excluded.
WITH monthly AS (
    SELECT
        date_trunc('month', i.invoiced_at)::date AS month,
        SUM(CASE WHEN l.row_type = 'sale' THEN l.quantity * l.unit_price ELSE 0 END) AS gross_sales,
        SUM(CASE WHEN l.row_type = 'cancellation' THEN l.quantity * l.unit_price ELSE 0 END) AS cancellations,
        SUM(l.quantity * l.unit_price) AS net_sales
    FROM invoice_lines AS l
    JOIN invoices AS i ON i.invoice_no = l.invoice_no
    WHERE l.row_type IN ('sale', 'cancellation')
    GROUP BY 1
)
SELECT
    month,
    ROUND(gross_sales, 2) AS gross_sales,
    ROUND(cancellations, 2) AS cancellations,
    ROUND(net_sales, 2) AS net_sales,
    ROUND(100.0 * (net_sales - LAG(net_sales) OVER (ORDER BY month))
          / NULLIF(LAG(net_sales) OVER (ORDER BY month), 0), 1) AS change_pct
FROM monthly
ORDER BY month;