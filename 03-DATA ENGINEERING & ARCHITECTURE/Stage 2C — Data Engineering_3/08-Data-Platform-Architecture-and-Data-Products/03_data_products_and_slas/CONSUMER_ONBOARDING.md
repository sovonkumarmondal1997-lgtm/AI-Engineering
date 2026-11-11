# Consumer onboarding — `orders` data product

## Purpose and supported use

`orders` publishes one curated row per order, including cancelled orders. It supports operational reporting, customer analytics, and order-level analysis. It is **not** the accounting system of record and `order_total` is not recognized revenue.

## Find and request access

1. Find `orders` in the catalogue entry recorded in `specs/orders.yaml`.
2. Review owner, classification, retention, schema, lineage, and changelog.
3. Request the least-privilege `orders-consumer` role through the organization's access workflow.
4. Use the support channel `#orders-data-support` for questions and incident reports.

## Contract and quality expectations

- Current contract version: `1.2.0`.
- Freshness: latest event age is at most 15 minutes for at least 99% of hourly probes in a rolling 30-day window.
- Completeness: actual rows / expected rows from the upstream delivery manifest is at least 99.5% for at least 99% of evaluated observations over 30 days.
- Unique/non-null `order_id`: no duplicates and no null IDs in a valid snapshot.
- Product schema and business semantics are defined in `specs/orders.yaml`.

The 99% SLO is evaluated separately for each SLI. A snapshot passing now does not prove the rolling-window SLO is met.

## Example query

```sql
SELECT order_status, COUNT(*) AS order_count
FROM lakehouse.analytics.orders
GROUP BY order_status
ORDER BY order_status;
```

## Breaking changes

Subscribe to the product's release/incident channel. The planned `2.0.0` change removes `order_status` and introduces `status_code`; it is breaking. The producer must publish a migration mapping, notify consumers, maintain the old version during the notice window, and retire it only after the published sunset date and consumer review.

## Incident response

Include product name/version, observation time, affected query/job, sample failing keys (avoid sending restricted values into public channels), expected versus actual result, and business impact. The producer owns triage for product defects; consumers own their downstream recovery and must be informed of material corrections.
