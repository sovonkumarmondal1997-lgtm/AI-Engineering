-- Generated from crm_customers (schema 3.0)
{{ config(materialized='view', tags=['customer', 'crm']) }}
select customer_id, email, full_name, updated_at
from {{ source('crm', 'customers') }}