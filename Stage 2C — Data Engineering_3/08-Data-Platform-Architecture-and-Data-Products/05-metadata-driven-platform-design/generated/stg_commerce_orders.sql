-- Generated from commerce_orders (schema 3.0)
{{ config(materialized='view', tags=['orders', 'commerce']) }}
select order_id, customer_id, amount, status
from {{ source('commerce', 'orders') }}