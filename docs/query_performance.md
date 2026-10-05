# Query Performance

Measured with `EXPLAIN ANALYZE` on 1,044,848 invoice lines (PostgreSQL 17, local Docker).

## Indexes

Foreign keys are not indexed automatically in PostgreSQL. Three indexes were added:

| Index | Used for |
|---|---|
| `invoice_lines (invoice_no)` | Lines of an invoice, joins to `invoices` |
| `invoice_lines (stock_code)` | Sales of a product, joins to `products` |
| `invoices (customer_id)` | Invoices of a customer |

## Results

| Query | Without index | With index |
|---|---|---|
| Lines of one invoice | 611 ms (Seq Scan) | 0.9 ms (Index Scan) |
| Purchase history of one customer (join) | 160 ms (Hash Join, Seq Scan) | 2.4 ms (Nested Loop, Index Scan) |
| Sales per product (full-table aggregate) | Seq Scan | Seq Scan (index not used) |

## Takeaways

- Indexes help selective queries that read a small part of a table.
- Full-table aggregations still read every row, so the planner correctly ignores the index.
- Indexes cost storage (37 MB for a 69 MB table) and slow down loading, so only columns used in lookups and joins are indexed.
- `ANALYZE` runs after each load so the planner has up-to-date statistics.