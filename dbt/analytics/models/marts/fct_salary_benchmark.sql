{{
    config(
        materialized='table',
        cluster_by=['experience_level', 'country']
    )
}}

with cleaned_salary as (
    select * from {{ ref('stg_salary_exp') }}
    where annual_salary > 500
)

select 
    country,
    annual_salary,
    case 
        when years_experience_pro <= 2 then 'Junior (0-2yrs)'
        when years_experience_pro <= 5 then 'Mid-Level (3-5yrs)'
        when years_experience_pro <= 10 then 'Senior (6-10yrs)'
        else 'Lead/Principal (11+yrs)'
    end as experience_level,
    years_experience_pro
from cleaned_salary