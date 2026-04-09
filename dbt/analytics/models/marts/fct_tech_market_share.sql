{{
    config(
        materialized='table',
        cluster_by=['developer_role']
    )
}}

select 
    developer_role,
    programming_language,
    total_tech_users,
    market_share_percentage
from {{ ref('stg_market_share') }}