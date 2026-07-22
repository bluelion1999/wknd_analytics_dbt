from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, RenderConfig
from cosmos.constants import LoadMode

DBT_PROJECT_PATH = "/opt/airflow/dbt/wknd_dbt_project"
DBT_EXECUTABLE_PATH = "/opt/airflow/dbt_venv/bin/dbt"

project_config = ProjectConfig(
    DBT_PROJECT_PATH,
    manifest_path=f"{DBT_PROJECT_PATH}/target/manifest.json",
)

profile_config = ProfileConfig(
    profile_name='wknd_analytics',
    target_name='dev',
    profiles_yml_filepath=f"{DBT_PROJECT_PATH}/profiles.yml"
)

execution_config = ExecutionConfig(
    dbt_executable_path=DBT_EXECUTABLE_PATH,
)

# Loading from a pre-generated manifest.json (built once during airflow-init,
# before the scheduler ever parses this DAG) instead of having Cosmos shell
# out to `dbt ls` at parse time: faster DAG parsing, and it reads dbt's own
# complete dependency graph directly rather than Cosmos re-deriving it.
#
# Cosmos's task graph still mirrors dbt's own DAG, which has no edge from
# seeds to source()-referencing models (source() just names an external
# table, it doesn't know a seed happens to produce it). So seeds are excluded
# here and run manually as an explicit upstream step instead.
render_config = RenderConfig(
    load_method=LoadMode.DBT_MANIFEST,
    exclude=["path:seeds"],
)

with DAG(
    dag_id="wknd_analytics_dbt_dag",
    schedule="@daily",
    start_date=datetime(2026, 7, 21),
    catchup=False,
    max_active_tasks=1,
) as dag:

    seed_task = BashOperator(
        task_id="dbt_seed",
        bash_command=(
            f"{DBT_EXECUTABLE_PATH} deps --project-dir {DBT_PROJECT_PATH} --profiles-dir {DBT_PROJECT_PATH} && "
            f"{DBT_EXECUTABLE_PATH} seed --project-dir {DBT_PROJECT_PATH} --profiles-dir {DBT_PROJECT_PATH} "
            f"--profile wknd_analytics --target dev"
        ),
    )

    dbt_task_group = DbtTaskGroup(
        group_id="dbt_wknd_analytics",
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        render_config=render_config,
        operator_args={"install_deps": True},
    )

    seed_task >> dbt_task_group
