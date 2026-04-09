{{ config(materialized='view') }}

with source as (
    select * from {{ source('stackoverflow_raw', 'stg_salary_exp_2025') }}
)

select
    ResponseId as response_id,
    nullif(Country, 'NA') as country,
    cast(Salary as float64) as annual_salary,
    cast(YearsCodePro as int64) as years_experience_pro,
    cast(YearsCode as int64) as years_experience_total
from source
where Country != 'NA'
    and Country is not null