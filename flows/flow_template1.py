"""Defines the {Flow Name} flow"""

# TODO: Fill in the flow name above

import os

from prefect import task, flow
from prefect.blocks.system import JSON

from ucb_prefect_tools import util, database, object_storage


@task
def to_csv(dataframe):
    """Takes a dataframe and returns bytes for the data in CSV format"""

    # This is an example task
    # Function parameters should provide all that is needed to run this task
    # Try to return in-memory data: if you do have to save something to disk, return the filenames
    # This way, inputs, outputs, and functional modes are clearly visible

    return dataframe.to_csv(index=False).encode("utf-8")


# Keep the get_config task close to the flow definition for readability
@task
def get_config(env_name):
    """Returns a dict of env variables for the given env_name."""

    config = {}
    # Note that the 'config' dict uses generic names for source/sink systems
    # That way if a system needs to be swapped out, you just change one line

    # TODO: Replace with your own configuration
    if env_name == "prod":
        config["source_database"] = JSON.load("edb-prod-connection").value
        config["sink_storage"] = JSON.load("cutransfer-info").value
        config["sink_filepath"] = "../../user/ITS/OIT_USE_E_SIGN.CSV"

    elif env_name == "dev":
        config["source_database"] = JSON.load("edb-dev-connection").value
        config["sink_storage"] = JSON.load("ds-file-delivery-dev-connection").value
        config["sink_filepath"] = "test/buff_portal/OIT_USE_E_SIGN.CSV"

    else:
        raise ValueError(f"Unrecognized environment name: {repr(env_name)}")

    # This line replaces values such as "<secret>edb-prod-pw" with the value of the Secret Block
    # named "edb-prod-pw"
    return util.reveal_secrets(config)


# TODO: Fill in flow name below. E.g. "Cornerstone - Users"
@flow(
    name="Repo Name - Flow Name",
    timeout_seconds=8 * 3600,
)
def main_flow(env: str = "dev"):
    """Enter flow description here"""

    with util.limit_concurrency(max_tasks=10):

        # TODO: Fill in flow description in function docstring.

        config = get_config(env)

        # TODO: Replace statements below with your own ETL tasks and/or SQL statements

        select_sql = r"""
            SELECT TO_CHAR(emplid) AS "EMPLID"
                ,eff_status AS "STATUS"
                ,TO_CHAR(lastupddttm) AS "LASTUPDDTTM"
            FROM USE.e_sign
            WHERE (lastupddttm > sysdate - 4)
            ORDER BY 2 DESC
        """

        data = database.sql_extract.submit(
            sql_query=select_sql, connection_info=config["source_database"]
        )
        csv_file = to_csv.submit(data)
        object_storage.put.submit(
            binary_object=csv_file,
            object_name=config["sink_filepath"],
            connection_info=config["sink_storage"],
        )


# Allow command-line interface for deployments, etc. Syntax:
# `python example_flow.py deploy`
if __name__ == "__main__":
    util.run_flow_command_line_interface(
        flow_filename=os.path.basename(__file__), flow_function_name="main_flow"
    )
