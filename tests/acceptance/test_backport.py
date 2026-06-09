import os
import re
import subprocess
from pathlib import Path
import pytest

# Fallbacks for local testing if CI env vars aren't present
CI_REPOSITORY_URL = os.getenv(
    "CI_REPOSITORY_URL", "https://github.com/mendersoftware/meta-mender.git"
)
RECIPE_PATTERN = r"^mender(-[a-z0-9-]+)?_([0-9]+)\.[0-9]+\.[0-9]+\.bb$"


@pytest.fixture(scope="session")
def master_recipes(tmp_path_factory):
    """Clones the master branch to a temp directory and extracts recipe data."""
    # Create a unique session-wide temp directory
    repo_dir = tmp_path_factory.mktemp("master_branch_ref")

    # Clone master branch
    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            "master",
            CI_REPOSITORY_URL,
            str(repo_dir),
        ],
        check=True,
        capture_output=True,
    )

    # Find and process recipes using native Python instead of a complex shell pipeline
    latest_recipes = {}
    for path in repo_dir.rglob("*.bb"):
        filename = path.name
        match = re.match(RECIPE_PATTERN, filename)
        if match:
            major_version = int(match.group(2))
            base_name = match.group(1) or "core"  # Group by variant components

            # Keep track of the highest major version found for this component type
            if (
                base_name not in latest_recipes
                or major_version > latest_recipes[base_name]["major_version"]
            ):
                latest_recipes[base_name] = {
                    "recipe": filename,
                    "major_version": major_version,
                }

    # Return a dictionary mapped by filename for O(1) lookups later
    return {item["recipe"]: item["major_version"] for item in latest_recipes.values()}


@pytest.fixture(scope="session")
def commit_recipes():
    """Gets the recipes modified or added in the current Git HEAD."""
    cmd = [
        "git",
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "--root",
        "-m",
        "HEAD",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    commit_files = set(result.stdout.strip().splitlines())

    recipes = []
    for filepath in commit_files:
        filename = os.path.basename(filepath)
        match = re.match(RECIPE_PATTERN, filename)
        if match:
            recipes.append({"recipe": filename, "major_version": int(match.group(2))})
    return recipes


def test_backport_preference(master_recipes, commit_recipes):
    """Validates that backported major bumps include DEFAULT_PREFERENCE = '-1'."""
    if not commit_recipes:
        pytest.skip("No mender recipes found in this commit.")

    failed_recipes = []

    for commit_item in commit_recipes:
        filename = commit_item["recipe"]

        # Check if this exact file existed in master
        if filename in master_recipes:
            master_version = master_recipes[filename]
            commit_version = commit_item["major_version"]

            # If the current commit features a higher major version than master if commit_version > master_version: Use git grep to see if DEFAULT_PREFERENCE is set to "-1"
                grep_cmd = [
                    "git",
                    "grep",
                    "-q",
                    "-E",
                    r"^[[:space:]]*DEFAULT_PREFERENCE = ['\"]-1['\"]",
                    "HEAD",
                    "--",
                    f"*{filename}",
                ]
                grep_result = subprocess.run(
                    grep_cmd, capture_output=False, check=False
                )

                if grep_result.returncode != 0:
                    failed_recipes.append(filename)

    assert not failed_recipes, (
        f"The following backported recipes are missing "
        f'DEFAULT_PREFERENCE = "-1": {failed_recipes}'
    )
