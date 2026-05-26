#!/usr/bin/python
# Copyright 2026 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

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

    # Find and process recipes
    latest_recipes = {}
    for path in repo_dir.rglob("*.bb"):
        filename = path.name
        match = re.match(RECIPE_PATTERN, filename)
        if match:
            major_version = int(match.group(2))
            base_name = match.group(1)

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
    return {
        base_name: item["major_version"] for base_name, item in latest_recipes.items()
    }


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
            base_name = match.group(1)
            recipes.append(
                {
                    "recipe": filename,
                    "base_name": base_name,
                    "major_version": int(match.group(2)),
                }
            )

    return recipes


def test_default_preference(master_recipes, commit_recipes):
    """Validates that backported major bumps include DEFAULT_PREFERENCE = '-1'."""
    if not commit_recipes:
        pytest.skip("No mender recipes found in this commit.")

    failed_recipes = []

    for commit_item in commit_recipes:
        filename = commit_item["recipe"]
        base_name = commit_item["base_name"]
        commit_version = commit_item["major_version"]

        # Check if this exact file existed in master
        if base_name in master_recipes:
            master_version = master_recipes[base_name]

            # If the current commit features a higher major version than master
            if commit_version > master_version:
                # Use git grep to see if DEFAULT_PREFERENCE is set to "-1"
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
