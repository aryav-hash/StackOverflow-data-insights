{{ config(materialized='view') }}

with source as (
    select * from {{ source('stackoverflow_raw', 'stg_market_share_2025') }}
)

select 
    nullif(DevType, 'NA') as developer_role,
    nullif(Language, 'NA') as programming_language,
    cast(TechUsers as int64) as total_tech_users,
    cast(MarketSharePct as float64) as market_share_percentage
from source
where Language != 'NA'
    and Language is not null
    and DevType != 'NA'
    and DevType is not null