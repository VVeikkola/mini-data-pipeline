-- Business question: Which countries generate the most sales, and what share of the total do they have?
WITH country_sales AS (
    SELECT
        i.country,
        COUNT(DISTINCT i.invoice_no) AS invoices,
        SUM(l.quantity * l.unit_price) AS net_sales
    FROM invoice_lines AS l
    JOIN invoices AS i ON i.invoice_no = l.invoice_no
    WHERE l.row_type IN ('sale', 'cancellation')
    GROUP BY i.country
)
SELECT
    country,
    invoices,
    ROUND(net_sales, 2) AS net_sales,
    ROUND(100.0 * net_sales / SUM(net_sales) OVER (), 1) AS share_pct
FROM country_sales
ORDER BY net_sales DESC
LIMIT 10;