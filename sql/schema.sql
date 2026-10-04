DROP TABLE IF EXISTS invoice_lines;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS rejected_rows;

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY
);

CREATE TABLE products (
    stock_code  TEXT PRIMARY KEY,
    description TEXT
);

CREATE TABLE invoices (
    invoice_no  TEXT PRIMARY KEY,
    customer_id TEXT REFERENCES customers (customer_id),
    invoiced_at TIMESTAMP NOT NULL,
    country     TEXT
);

CREATE TABLE invoice_lines (
    line_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_no TEXT NOT NULL REFERENCES invoices (invoice_no),
    stock_code TEXT NOT NULL REFERENCES products (stock_code),
    quantity   INTEGER NOT NULL CHECK (quantity <> 0),
    unit_price NUMERIC(10,3) NOT NULL,
    row_type   TEXT NOT NULL CHECK (row_type IN (
        'sale', 'cancellation', 'stock_adjustment',
        'accounting_adjustment', 'non_product'
    )),
    CHECK (unit_price >= 0 OR row_type = 'accounting_adjustment')
);

CREATE TABLE rejected_rows (
    rejected_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reject_reason TEXT NOT NULL,
    invoice       TEXT,
    stock_code    TEXT,
    description   TEXT,
    quantity      TEXT,
    invoice_date  TEXT,
    price         TEXT,
    customer_id   TEXT,
    country       TEXT
);
