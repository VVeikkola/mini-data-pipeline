# Data Contract: Online Retail II

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
| Data owner contact | Not reachable. Rules are based on public documentation and [profiling](data_profiling.md) |
| Contract version | 0.2 |

**Note:** Column names in the UCI documentation differ from the actual file
(`InvoiceNo` → `Invoice`, `UnitPrice` → `Price`, `CustomerID` → `Customer ID`).
This contract uses the names found in the file.

## 2. File level

| Sheet | Rows | Min InvoiceDate | Max InvoiceDate |
|---|---|---|---|
| Year 2009-2010 | 525,461 | 2009-12-01 07:45:00 | 2010-12-09 20:01:00 |
| Year 2010-2011 | 541,910 | 2010-12-01 08:26:00 | 2011-12-09 12:50:00 |

- **Known issue:** Sheets overlap on 2010-12-01 – 2010-12-09. Extract keeps the rows from the first sheet and removes 22,523 overlapping rows from the second.
- **Pipeline input:** `data/combined_retail_data.csv`. UTF-8, delimiter `,`, header row, `\n` line endings, decimal separator `.`, timestamps `YYYY-MM-DD HH:MM:SS`. Raw values, no transformations.

## 3. Grain and business key

- **Grain:** one row = one line on an invoice. The same `StockCode` can appear on the same invoice more than once.
- **Business key:** the source has no unique row identifier. (`Invoice`, `StockCode`) is not unique.

### Duplicate definitions

| Type | Definition | Handling | Rationale |
|---|---|---|---|
| Key duplicate | Same `Invoice` + `StockCode`, other fields differ | Allowed | Separate add-to-cart events, both are real lines |
| Exact duplicate | All fields identical | Keep, WARN | Cannot distinguish a double write from a genuine repeat |

## 4. Columns

| Column | Type | Required | Rule | Example | Violation handling |
|---|---|---|---|---|---|
| Invoice | text | yes | 6 digits, optionally prefixed with `C` or `A` | `489434`, `C489449`, `A506401` | Missing or other format → REJECT |
| StockCode | text | yes | Non-empty code, upper case | `85123A`, `15056BL`, `POST` | Missing → REJECT. Lower case → FIX |
| Description | text | no | Trimmed | `WHITE CHERRY LIGHTS` | Extra whitespace → FIX |
| Quantity | integer | yes | ≠ 0 | `12`, `-3` | Missing, non-integer or 0 → REJECT |
| InvoiceDate | timestamp | yes | Valid, not in the future | `2010-12-01 08:26:00` | Missing or invalid → REJECT. In the future → WARN |
| Price | decimal | yes | Unit price in GBP (£), ≥ 0 | `2.55` | Missing → REJECT. < 0 outside accounting adjustments → REJECT |
| Customer ID | text | no | 5 digits. NULL = unknown customer | `13085` | Format `13085.0` → FIX |
| Country | text | no | Country where the customer resides | `France` | Missing → WARN |

**REJECT** means the row cannot be loaded. Valid rows that are not sales are kept and classified (section 5).

## 5. Row classification

Every loaded row gets a `row_type`. Rules are applied in order; the first match wins.

| Order | `row_type` | Rule |
|---|---|---|
| 1 | `accounting_adjustment` | `Invoice` starts with `A` |
| 2 | `non_product` | `StockCode` is a known non-product code (e.g. `POST`, `DOT`, `M`, `D`, `C2`, `S`, `BANK CHARGES`, `ADJUST`, `AMAZONFEE`, `gift_0001_*`) |
| 3 | `cancellation` | `Invoice` starts with `C` |
| 4 | `stock_adjustment` | `Quantity` < 0 and `Price` = 0 |
| 5 | `sale` | Everything else |

- Order matters: a cancelled postage line is `non_product`, not `cancellation`, so it does not reduce product sales.
- Sales metrics use `sale` and `cancellation`.
- The full list of non-product codes is maintained in code (Task 7).

## 6. Group-level rules

| Group | Rule | Handling | Profiling result |
|---|---|---|---|
| Invoice | Same `Customer ID` on all rows | WARN | 0 violations |
| Invoice | Same `Country` on all rows | WARN | 0 violations |
| Invoice | Same `InvoiceDate` on all rows | WARN. Invoice timestamp = earliest row timestamp | 83 invoices, max 9 min |
| StockCode | One product name | Product name = most frequent description | 1,232 codes have several descriptions (stock notes) |

## 7. Dataset-level rules

| Rule | Handling |
|---|---|
| Source file SHA256 matches the expected value | Stop the run |
| Overlap row counts are equal in both sheets | Stop the run |
| Input contains at least one row | Stop the run |

## 8. Assumptions and open questions

### Assumptions
- Missing `Customer ID` = unknown or unregistered customer. Supported by profiling: missing customer is always invoice-level.
- Key duplicates are separate add-to-cart events.
- `InvoiceDate` is UK local time.
- `InvoiceDate` differences within an invoice come from entry time or lines added shortly after. The chosen invoice timestamp is correct under both explanations.

### Open questions
- How is a row identified when the pipeline is re-run? (Task 9)
- Cancellation invoices do not reference the original invoice. The link can only be inferred.
- Are gift voucher sales product sales or a liability?

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-01 | Initial draft based on UCI documentation |
| 0.2 | 2026-10-02 | Updated after profiling: row classification, REJECT only for unloadable rows, verified group rules |