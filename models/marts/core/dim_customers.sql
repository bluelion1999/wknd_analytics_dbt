with customers as (
    select * from {{ref('stg_wknd__customers')}}
)

select 
    *,
    {{ days_between('signup_date','current_date') }} as customer_tenure_days
from 
    customers