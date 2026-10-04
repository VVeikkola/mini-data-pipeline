-- Data quality: Does every row belong to exactly one row type, and do the parts add up to the total?
-- If the two total_value columns differ, rows were lost or double counted.
WITH by_type AS (
    SELECT
        row_type,
        COUNT(*) AS lines,
        SUM(quantity) AS units,
        SUM(quantity * unit_price) AS value
    FROM invoice_lines
    GROUP BY ROLLUP (row_type)
)
SELECT
    COALESCE(row_type, 'TOTAL (sum of types)') AS row_type,
    lines,
    units,
    ROUND(value, 2) AS value
FROM by_type
UNION ALL
SELECT
    'TOTAL (whole table)',
    COUNT(*),
    SUM(quantity),
    ROUND(SUM(quantity * unit_price), 2)
FROM invoice_lines
ORDER BY lines DESC;