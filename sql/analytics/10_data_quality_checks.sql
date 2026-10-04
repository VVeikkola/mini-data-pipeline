-- Data quality: Checks that should all return 0 after a successful pipeline run.
SELECT 'lines without an invoice' AS check_name, COUNT(*) AS violations
FROM invoice_lines AS l
LEFT JOIN invoices AS i ON i.invoice_no = l.invoice_no
WHERE i.invoice_no IS NULL

UNION ALL
SELECT 'invoices without lines', COUNT(*)
FROM invoices AS i
LEFT JOIN invoice_lines AS l ON l.invoice_no = i.invoice_no
WHERE l.invoice_no IS NULL

UNION ALL
SELECT 'negative price outside accounting adjustments', COUNT(*)
FROM invoice_lines
WHERE unit_price < 0 AND row_type <> 'accounting_adjustment'

UNION ALL
SELECT 'cancellation lines with positive quantity', COUNT(*)
FROM invoice_lines
WHERE row_type = 'cancellation' AND quantity > 0

UNION ALL
SELECT 'last pipeline run not successful', COUNT(*)
FROM (
    SELECT status FROM pipeline_runs ORDER BY run_id DESC LIMIT 1
) AS last_run
WHERE status <> 'success';