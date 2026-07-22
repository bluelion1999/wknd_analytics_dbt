{%macro days_between(start_date, end_date) %}
    datediff('day', {{start_date}}, {{end_date}})
{% endmacro %}