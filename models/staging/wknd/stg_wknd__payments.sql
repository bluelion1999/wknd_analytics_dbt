with source as (
    select * from {{ source('wknd', 'raw_payments')}}
),

renamed as (
    select 
        payment_id,
        booking_id,
        payment_method,
        cast(amount_usd as decimal(10,2)) as amount_usd,
        cast(payment_date as date) as payment_date,
        payment_status
    from 
        source
)

select * from renamed