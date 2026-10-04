-- Business question: What are the 3 best-selling products in each of the 5 largest markets?
WITH top_countries AS (
    SELECT i.country
    FROM invoice_lines AS l
    JOIN invoices AS i ON i.invoice_no = l.invoice_no
    WHERE l.row_type IN ('sale', 'cancellation')
    GROUP BY i.country
    ORDER BY SUM(l.quantity * l.unit_price) DESC
    LIMIT 5
),
product_sales AS (
    SELECT
        i.country,
        l.stock_code,
        SUM(l.quantity * l.unit_price) AS net_sales
    FROM invoice_lines AS l
    JOIN invoices AS i ON i.invoice_no = l.invoice_no
    WHERE l.row_type IN ('sale', 'cancellation')
      AND i.country IN (SELECT country FROM top_countries)
    GROUP BY i.country, l.stock_code
),
ranked AS (
    SELECT
        country,
        stock_code,
        net_sales,
        RANK() OVER (PARTITION BY country ORDER BY net_sales DESC) AS sales_rank
    FROM product_sales
)
SELECT r.country, r.sales_rank, r.stock_code, p.description, ROUND(r.net_sales, 2) AS net_sales
FROM ranked AS r
JOIN products AS p ON p.stock_code = r.stock_code
WHERE r.sales_rank <= 3
ORDER BY r.country, r.sales_rank;