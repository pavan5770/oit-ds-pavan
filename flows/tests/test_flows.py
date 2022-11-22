"""Defines tests"""

# from prefect.logging import disable_run_logger

# from flows import my_flow


# def dataframes_are_equal(left, right):
#     """Asserts the two dataframes have equal values. Useful for checking task output."""

#     assert left.to_dict("records") == right.to_dict("records")


def test_some_task():
    """Tests some task. If you have nothing to test, leave this here.

    Follow best practices for unit tests, meaning each test should:
        - be focused on a single scenario for a single task/function
        - be isolated from external conditions
        - finish quickly
        - not test basic functionality of other packages like pandas or ucb_prefect_tools

    Use the `fn` attribute of a task to directly invoke its function for testing purposes. Use
    `disable_run_logger` if your task uses logging to avoid errors."""

    # with disable_run_logger():
    #     expected = "some value"
    #     actual = my_flow.my_task.fn()
    #     assert expected == actual
