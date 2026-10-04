-- Business question: Which 10 products bring in the most net sales?
SELECT
    p.stock_code,
    p.description,
    SUM(l.quantity) AS units_sold,
    ROUND(SUM(l.quantity * l.unit_price), 2) AS net_sales
FROM invoice_lines AS l
JOIN products AS p ON p.stock_code = l.stock_code
WHERE l.row_type IN ('sale', 'cancellation')
GROUP BY p.stock_code, p.description
ORDER BY net_sales DESC
LIMIT 10;