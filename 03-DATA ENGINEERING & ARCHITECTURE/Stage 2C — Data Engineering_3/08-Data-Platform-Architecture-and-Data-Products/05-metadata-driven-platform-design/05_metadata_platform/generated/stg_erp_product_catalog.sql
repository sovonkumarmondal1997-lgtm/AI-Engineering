-- Generated from erp_product_catalog (schema 2.0)
{{ config(materialized='view', tags=['product', 'catalog']) }}
select sku, name, category, modified_at
from {{ source('erp', 'product_catalog') }}