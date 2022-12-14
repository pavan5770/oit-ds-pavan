"""Defines the {Flow Name} flow"""

# TODO: Fill in the flow name above

import os
import pandas as pd
from datetime import datetime
from math import ceil

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

    return dataframe.to_csv('results.csv', index=False).encode("utf-8")


def readFlat(file):
    """ Takes a flat file and returns a dataframe """

    return pd.read_csv(file)


def ageCalc(dob):
    """ calculate age - takes a dataframe column as input and returns calculated age """

    # today's date in a list format
    today = datetime.now()
    # extract the timedelta from the date
    date1 = datetime.strptime(dob, r"%m/%d/%y")
    # calculate days and convert them to years
    return ceil((today - date1).days / 365)


def rowLevelDuplications(string1):
    """ split the string, remove the duplicate and join once again """

    # split the string by semicolon
    givenstring = string1.split(";")
    # create an empty list
    splitstore = []
    # loop through the given string and add only if it is not in the splitstore
    for item in givenstring:
        if item not in splitstore:
            splitstore.append(item)

    return ';'.join(splitstore)


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

        enrollments = readFlat("../test-data/enrollments.csv")

        students = readFlat("../test-data/students.csv")

        results = students.merge(
            enrollments,
            how="inner",
            on=["term_id", "student_id"],
        )

        results = results[results['credits_earned'] > 90]

        results['age'] = results['date_of_birth'].apply(ageCalc)

        results[['course_subject', 'placeholder', 'course_number', 'course_section']] = results['class_id'].str.split(
            "-", expand=True)

        results.drop(['placeholder'], axis=1)

        res1 = results[['student_id', 'major']].groupby(['student_id'])['major'].apply(';'.join).reset_index()

        res1['academic_plans'] = res1['major'].apply(rowLevelDuplications)

        res1.drop(['major'], axis=1)

        results = results.merge(
            res1,
            how="left",
            on=["student_id"]
        )

        results.drop(['major'], axis=1)

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
        csv_file = to_csv.submit(results)

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
