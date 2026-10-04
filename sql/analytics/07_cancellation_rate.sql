-- Business question: Which products have the highest cancellation rate?
-- Only products with meaningful sales (at least 1,000 GBP gross) are included.
WITH product_totals AS (
    SELECT
        stock_code,
        SUM(CASE WHEN row_type = 'sale' THEN quantity * unit_price ELSE 0 END) AS gross_sales,
        -SUM(CASE WHEN row_type = 'cancellation' THEN quantity * unit_price ELSE 0 END) AS cancelled
    FROM invoice_lines
    WHERE row_type IN ('sale', 'cancellation')
    GROUP BY stock_code
    HAVING SUM(CASE WHEN row_type = 'sale' THEN quantity * unit_price ELSE 0 END) >= 1000
)
SELECT
    t.stock_code,
    p.description,
    ROUND(t.gross_sales, 2) AS gross_sales,
    ROUND(t.cancelled, 2) AS cancelled,
    ROUND(100.0 * t.cancelled / t.gross_sales, 1) AS cancellation_rate_pct
FROM product_totals AS t
JOIN products AS p ON p.stock_code = t.stock_code
ORDER BY cancellation_rate_pct DESC
LIMIT 10;