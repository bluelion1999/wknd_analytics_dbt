with bookings as (
    select * from {{ ref('stg_wknd__bookings')}}
),

payments as (
    select * from {{ ref('stg_wknd__payments')}}
),

payment_agg as (
    select 
        booking_id,
        SUM(amount_usd) as total_paid_usd,
        COUNT(1) as payment_count,
        MAX(payment_date) as last_payment_date,
        bool_or(payment_status = 'refunded') as has_refund
    from   
        payments
    group by
        booking_id

)

select 
    bookings.*,
    coalesce(payment_agg.total_paid_usd, 0) as total_paid_usd,
    coalesce(payment_agg.payment_count, 0) as payment_count,
    payment_agg.last_payment_date,
    coalesce(payment_agg.has_refund, false) as has_refund
from 
    bookings
LEFT JOIN payment_agg
    ON bookings.booking_id = payment_agg.booking_id