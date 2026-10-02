DROP TABLE IF EXISTS invoice_lines;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

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
