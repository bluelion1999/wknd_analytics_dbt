with source as (
    select * from {{ source('wknd', 'raw_adventures')}}
),

renamed as (
    select 
        adventure_id,
        adventure_name,
        category,
        difficulty,
        cast(price_usd as decimal(10,2)) as price_usd,
        cast(duration_days as integer) as duration_days,
        location,
        cast(is_active as boolean) as is_active
    from 
        source
)

select * from renamed