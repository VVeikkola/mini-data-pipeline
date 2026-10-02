# Data Profiling: Online Retail II

Profiling of `data/combined_retail_data.csv` against [data contract](data_contract.md) v0.1.
Notebook: [`notebooks/01_data_profiling.ipynb`](../notebooks/01_data_profiling.ipynb)

## Summary

| Metric | Value |
|---|---|
| Source rows (two sheets) | 1,067,371 |
| Overlap rows removed in extract | 22,523 |
| Rows profiled | 1,044,848 |
| Invoices | 53,628 |

The data contains **several row types**, not only sales. Most surprises come from rows
that are valid but are not product sales.

## Key findings

### 1. Sheet overlap (fixed in extract)
Sheets overlap on 2010-12-01 – 2010-12-09. A naive concat had 34,335 exact duplicates;
removing the 22,523 overlap rows left 11,812, so **every removed row was an exact duplicate**.

### 2. Missing values
| Column | Missing | Note |
|---|---|---|
| Customer ID | 235,287 (22.5 %) | Invoice-level: no invoice mixes known and missing customer |
| Description | 4,275 (0.4 %) | All on zero-price rows (not sales) |

### 3. Duplicates
| Type | Extra rows | Decision |
|---|---|---|
| Exact duplicate | 11,812 (1.1 %) | Keep, WARN |
| Key duplicate (Invoice + StockCode) | 23,424 (2.2 %) | Allowed; 11,612 differ in another field |

### 4. Group consistency
| Rule | Violations | Decision |
|---|---|---|
| One Customer ID per invoice | 0 | OK |
| One Country per invoice | 0 | OK |
| One InvoiceDate per invoice | 83 (80 × 1 min, max 9 min, none cross a day) | WARN; use earliest timestamp |
| One Description per StockCode | 1,232 codes | Description also holds stock notes; use most frequent |

### 5. Row types discovered
| Row type | How to recognise | Rows | Note |
|---|---|---|---|
| Sale | Regular invoice, product code, price > 0 | majority | |
| Cancellation | `Invoice` starts with `C` | 19,165 | Does not reference the original invoice |
| Stock adjustment | Negative quantity, no `C`, price 0 | 3,393 | No customer, notes like "damaged", "missing". −569,314 units |
| Accounting adjustment | `Invoice` starts with `A` | 6 | "Adjust bad debt", net −£147,614.08 |
| Non-product line | `StockCode` in a known list (`POST`, `DOT`, `M`, `D`, `C2`, `BANK CHARGES`, `AMAZONFEE`, ...) | ~7,000 | Fees, postage, manual entries |

### 6. Other findings
- `Quantity = 0`: 0 rows, OK
- Extreme quantity ±80,995: order `581483` cancelled 12 min later by `C581484` (£168,469.60)
- Only 1 row has positive quantity on a `C` invoice (`M` / Manual, £373.57)
- Product codes can have two-letter suffixes (`15056BL`) and mixed case (`15056bl`)
- Some descriptions have leading whitespace (`" WHITE CHERRY LIGHTS"`)
- UCI documentation column names differ from the file

## Decisions for contract v0.2
1. Introduce `row_type` classification. REJECT only rows that cannot be loaded.
2. Identify non-product lines with a list of known codes, not a format rule.
3. Normalise `StockCode` to upper case and trim `Description`.
4. Invoice timestamp = earliest row timestamp.