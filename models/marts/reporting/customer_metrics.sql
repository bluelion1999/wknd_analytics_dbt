with customers as (
    select * from {{ref('dim_customers')}}
),

bookings as (
    select * from {{ref('fct_bookings')}}
)

select 
    customers.customer_id,
    customers.first_name,
    customers.last_name,
    count(bookings.booking_id) as total_bookings,
    count(1) filter (where bookings.status = 'completed') as completed_bookings,
    count(1) filter (where bookings.status = 'cancelled') as cancelled_bookings,
    coalesce(sum(bookings.total_paid_usd), 0) as total_spent_usd,
    sum(bookings.avg_rating * bookings.review_count) / nullif(sum(bookings.review_count), 0) as avg_rating_given,
    min(bookings.booking_date) as first_booking_date,
    max(bookings.booking_date) as last_booking_date,
    count(bookings.booking_id) > 1 as is_repeat_customer
from 
    customers
left join bookings 
    on customers.customer_id = bookings.customer_id 
group by 
    customers.customer_id, customers.first_name, customers.last_name