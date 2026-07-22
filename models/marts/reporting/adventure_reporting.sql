
with adventures as (
    select * from {{ ref('dim_adventures')}}
),
bookings as (
    select * from {{ ref('fct_bookings')}}
),
metrics as (
    select
        adventures.adventure_id,
        adventures.adventure_name,
        adventures.category,
        count(bookings.booking_id) as total_bookings,
        count(1) filter (where bookings.status = 'cancelled') as cancelled_bookings,
        count(1) filter (where bookings.status = 'cancelled') / nullif(count(bookings.booking_id), 0) as cancellation_rate,
        coalesce(sum(bookings.total_paid_usd), 0) as total_revenue_usd,
        sum(avg_rating * review_count) / nullif(sum(review_count), 0) as avg_rating
    from 
        adventures 
    left join bookings 
            on adventures.adventure_id = bookings.adventure_id 
    group by 
        adventures.adventure_id, adventures.adventure_name, adventures.category
)

select 
    *,
    dense_rank() over (order by total_revenue_usd desc) as revenue_rank
from 
    metrics