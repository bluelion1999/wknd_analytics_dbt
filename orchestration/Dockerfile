FROM apache/airflow:2.10.3-python3.11

# dbt is installed into its own virtualenv, separate from Airflow's Python
# environment. This is the pattern astronomer-cosmos recommends: dbt-core's
# pinned dependencies frequently conflict with Airflow's, so isolating them
# avoids dependency resolution failures in the main Airflow image.
RUN python3 -m venv /opt/airflow/dbt_venv && \
    /opt/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-core==1.12.* dbt-duckdb==1.10.*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Baked into the image (not a mounted volume) so it's owned by the airflow
# user from the start -- a fresh Docker named volume would default to root
# ownership, which the non-root airflow user can't write into.
RUN mkdir -p /opt/airflow/dbt/wknd_dbt_project/data /opt/airflow/dbt/wknd_dbt_project/target
