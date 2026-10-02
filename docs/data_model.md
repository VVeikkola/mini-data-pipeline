# Data Model

```mermaid
erDiagram
    CUSTOMERS |o--o{ INVOICES : places
    INVOICES ||--|{ INVOICE_LINES : contains
    PRODUCTS ||--o{ INVOICE_LINES : "appears on"

    CUSTOMERS {
        text customer_id PK
    }
    PRODUCTS {
        text stock_code PK
        text description "most frequent description"
    }
    INVOICES {
        text invoice_no PK
        text customer_id FK "NULL = unknown customer"
        timestamp invoiced_at "earliest row timestamp"
        text country
    }
    INVOICE_LINES {
        bigint line_id PK
        text invoice_no FK
        text stock_code FK
        integer quantity "not 0"
        numeric unit_price "GBP, 3 decimals"
        text row_type "sale, cancellation, ..."
    }
```

## Design decisions

| Decision | Reason |
|---|---|
| `country` on invoices, not customers | 13 customers have several countries; country is consistent within every invoice |
| Surrogate key `line_id` | Source has no unique row identifier |
| `row_type` on lines | One invoice can mix product and non-product lines |
| `customer_id` nullable | 22.5 % of lines have no customer (invoice-level) |
| `unit_price` with 3 decimals | Some prices are £0.001 |

