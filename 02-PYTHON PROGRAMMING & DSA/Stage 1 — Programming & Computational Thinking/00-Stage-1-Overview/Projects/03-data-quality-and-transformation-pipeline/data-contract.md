# Data Contract — Orders CSV

The input header must contain exactly these fields, in any order: `order_id`, `customer_email`, `order_date`, `country`, `quantity`, `unit_price`, `status`.

- `order_id`: non-empty after trim; case-sensitive identity; first valid occurrence wins.
- `customer_email`: basic email shape; trim and lowercase.
- `order_date`: canonical real date `YYYY-MM-DD`.
- `country`: must exist in configured country mapping; output uppercase ISO-2 code.
- `quantity`: base-10 integer greater than zero; `2.0` is rejected.
- `unit_price`: finite, non-negative decimal with at most two fractional digits; `10.999` is rejected.
- `status`: one of `new`, `paid`, `shipped`, `cancelled`, lowercased.
- Derived fields: `order_total = quantity × unit_price`, `order_month = YYYY-MM`.

Missing, duplicate, or unexpected header columns fail the batch. A row with a field count different from the header is rejected. All field-level violations are collected. Reject rate is rejected input rows divided by all input data rows. A valid header-only file has zero rows and a zero reject rate. Invalid rows do not reserve duplicate IDs. Each reject entry contains a JSON-encoded copy of the raw row.
