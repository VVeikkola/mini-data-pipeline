# Data Contract

## 1. General

 | | |
|---|---|
| Dataset | Online Retail II |
| Source | [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii) |
| Creator | Daqing Chen |
| Published | 2019-09-20 |
| License | CC BY 4.0 (attribution required) |
| DOI | 10.24432/C5CG6D |
| Business context | UK-based online gift retailer, many customers are wholesalers |
| Period | 2009-12-01 – 2011-12-09 |
| Delivery | One-time manual download (`.xlsx`). Not committed to the repository |
| Data owner contact | Not reachable (ASSUMPTION: rules are based on public documentation and profiling) |
| Contract version | 0.1 (draft) |

**Note:** Column names in the UCI documentation differ from the actual file
(`InvoiceNo` → `Invoice`, `UnitPrice` → `Price`, `CustomerID` → `Customer ID`).
This contract uses the names found in the file.

## 2. File level
- **Format:** .xlsx
- **Names of sheets and rows:** Year 2009-2010: 525461, Year 2010-2011:541910
- **InvoiceDate max and min time:** Year 2009-2010 2009-12-01 07:45:00 2010-12-09 20:01:00, Year 2010-2011 2010-12-01 08:26:00 2011-12-09 12:50:00

## 3. Grain and Business key
- **Grain:** one row = one product line per invoice
- **Business key:** the source has no unique row identifier.
- **Duplicate Definitions:**
| Type | Definition | Handling | Rationale |
  |---|---|---|---|
  | Key duplicate | Same `Invoice` + `StockCode`, other fields differ | Allowed | Most likely separate add-to-cart events; both rows are real sales |
  | Exact duplicate | All fields identical | WARN, rows are kept | The data cannot distinguish a system double-write from a genuine repeat (ASSUMPTION) |
- **OPEN:** How is a row identified when the pipeline is re-run? To be resolved in Task 9.

## 4. Columns

| Column | Type | Required | Rule | Example | Violation handling |
|---|---|---|---|---|---|
| Invoice | text | yes | 6 digits, or `C` + 6 digits (= cancellation) | `489434`, `C489449` | Missing or invalid format → WARN |
| Quantity | integer | yes | ≠ 0. Negative only on cancellation invoices (`C`) | `12`, `-3` | Missing or 0 → REJECT. Negative without `C` invoice → WARN |
| Customer ID | text | no | 5 digits. NULL = unknown customer (ASSUMPTION) | `13085` | NULL → WARN. Format `13085.0` → FIX: strip decimal part |
| StockCode | text | yes | 5 digits, optionally followed by a letter | `85123A`, `71053` | Missing → WARN. Other format → WARN|
| Description | text | no | Leading/trailing whitespace trimmed | `RED WOOLLY HOTTIE WHITE HEART.` | Missing or empty → WARN. Extra whitespace → FIX |
| Price | decimal | yes | Unit price in GBP (£), > 0  | `23.50` | Missing or < 0 → REJECT. 0 → WARN |
| Country | text | no | Not empty. Country where the customer resides   | `France` | Missing → WARN |
| InvoiceDate | timestamp | yes | Valid timestamp, not in the future | `2010-12-01 08:26:00` | Missing or invalid → WARN. In the future → WARN |

## 5. Group-level rules

| Group | Rule | Violation handling |
|---|---|---|
| Invoice | Same `Customer ID` on all rows | Different values → WARN (rejecting would understate sales) |
| Invoice | Same `Country` on all rows | Different values → WARN |
| Invoice | Same `InvoiceDate` on all rows | Different values → WARN |
| StockCode | Same `Description` for each `StockCode` | Different values → WARN |

## 6. Data quality rules

| Rule | Violation handling |
|---|---|
| Negative `Quantity` is expected only on invoices whose `Invoice` starts with `C`, and `C` invoices are expected to have negative quantities | Mismatch in either direction → WARN and investigate |
| Input dataset must contain at least one row | Zero rows → REJECT the entire pipeline run |

## 7. Assumptions and open questions

### Assumptions

- **ASSUMPTION:** Missing `Customer ID` represents an unknown or unregistered customer rather than an invalid transaction.
- **ASSUMPTION:** Repeated `Invoice + StockCode` combinations may represent legitimate separate invoice lines and are not automatically duplicates.
- **ASSUMPTION:** Exact duplicate rows cannot safely be removed without understanding the source-system behavior.
- **ASSUMPTION:** `InvoiceDate` is recorded in UK local time.