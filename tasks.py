from invoke import task
from invoke.exceptions import Exit

APP = "app"
TESTS = "tests"
PYLINT_THRESHOLD = 9
PYTHON_CODE = "app/ tests/ migrations/ tasks.py"
MIN_COVERAGE = 50  # Need to increase this


def _insight_title(title: str):
    header_underline = "-" * len(title)
    print(f"{header_underline}\n{title}\n{header_underline}")


@task
def lint_app(context):
    """Runs Pylint on application code."""

    result = context.run(
        f"pylint --fail-under={PYLINT_THRESHOLD} {PYTHON_CODE}", warn=True, pty=True
    )

    if result.return_code:
        raise Exit(f"Pylint failed. It's score must be above {PYLINT_THRESHOLD}")


@task
def check_format(context):
    """Checks the app's format."""

    # 1. Check that all code is formatted using black
    context.run(f"black --check {PYTHON_CODE}")
    # 2. Check that all imports are ordered using isort
    context.run(f"isort {PYTHON_CODE} -c")


@task
def set_up_database(context):
    """Spins up database and migrates schemas."""

    context.run("/app/continuous_integration/manage_database.sh")


@task
def tests(context):
    """Runs all tests"""
    context.run(f"coverage run --source {APP} -m pytest {TESTS} --color=yes")
    context.run(f"coverage report --fail-under={MIN_COVERAGE}")
    context.run("coverage html")


@task
def ci(context):
    """Orchestrates continuous integration tasks"""

    _insight_title("LINTING CODE")
    lint_app(context)
    _insight_title("CHECKING CODE FORMAT")
    check_format(context)
    _insight_title("SETTING UP DATABASE")
    set_up_database(context)
    _insight_title("RUNNING TESTS")
    tests(context)
