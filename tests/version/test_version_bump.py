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
import json
import re
import subprocess
from pathlib import Path
import pytest

GITHUB_AUTH = os.getenv("GITHUB_AUTH")
CI_COMMIT_SHA = os.getenv("CI_COMMIT_SHA")
RECIPE_PATTERN = r"^mender(-[a-z0-9-]+)?_([0-9]+)\.[0-9]+\.[0-9]+\.bb$"
REPO_DIR = Path(__file__).resolve().parent.parent.parent

@pytest.fixture(scope="session")
def pr_num_from_sha():  # DONE!
    """Returns the pull request number."""
    cmd_curl = [
        "curl",
        "-s",
        "-H",
        f"Authorization: Bearer {GITHUB_AUTH}",
        f"https://api.github.com/search/issues?q=repo:mendersoftware/meta-mender+type:pr+sha:{CI_COMMIT_SHA}",
    ]

    cmd_jq = ["jq", "-r", ".items[0].number"]

    process_curl = subprocess.Popen(cmd_curl, stdout=subprocess.PIPE)

    process_jq = subprocess.run(
        cmd_jq, stdin=process_curl.stdout, capture_output=True, text=True
    )

    process_curl.stdout.close()
    process_curl.wait()

    pr_num = process_jq.stdout.strip()

    return pr_num


@pytest.fixture(scope="session")
def target_branch(pr_num_from_sha):  # DONE!
    """Returns the target branch of the pull request."""
    cmd_curl = [
        "curl",
        "-s",
        "-H",
        f"Authorization: Bearer {GITHUB_AUTH}",
        f"https://api.github.com/repos/mendersoftware/meta-mender/pulls/{pr_num_from_sha}",
    ]

    cmd_jq = ["jq", "-r", ".base.ref"]

    process_curl = subprocess.Popen(cmd_curl, stdout=subprocess.PIPE)

    process_jq = subprocess.run(
        cmd_jq, stdin=process_curl.stdout, capture_output=True, text=True
    )

    process_curl.stdout.close()
    process_curl.wait()

    target_branch = process_jq.stdout.strip()

    return target_branch


@pytest.fixture(scope="session")
def master_recipes():
    """Gets the master branch recipe data."""

    current_ref = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    if current_ref == "HEAD":
        current_ref = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    subprocess.run(
        ["git", "checkout", "master"],
        cwd=REPO_DIR,
        check=True,
        capture_output=True,
    )

    # Find and process recipes
    latest_recipes = {}
    for path in Path(REPO_DIR).rglob("*.bb"):
        filename = path.name
        match = re.match(RECIPE_PATTERN, filename)
        if match:
            major_version = int(match.group(2))
            suffix = match.group(1) if match.group(1) else ""
            base_name = f"mender{suffix}"

            # Keep track of the highest major version found for this component type
            if (
                base_name not in latest_recipes
                or major_version > latest_recipes[base_name]["major_version"]
            ):
                latest_recipes[base_name] = {
                    "recipe": filename,
                    "major_version": major_version,
                }

    # Switch back to original PR commit state
    subprocess.run(
        ["git", "checkout", current_ref],
        cwd=REPO_DIR,
        check=True,
        capture_output=True,
    )

    # Return a dictionary mapped by filename
    return {
        base_name: item["major_version"] for base_name, item in latest_recipes.items()
    }


@pytest.fixture(scope="session")
def commit_recipes(pr_num_from_sha):
    """Gets the recipes modified or added in the pull request."""

    cmd = [
        "curl",
        "-L",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"Authorization: Bearer {GITHUB_AUTH}",
        "-H",
        "X-GitHub-Api-Version: 2026-03-10",
        f"https://api.github.com/repos/mendersoftware/meta-mender/pulls/{pr_num_from_sha}/files",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    recipes = []

    try:
        files_json = json.loads(result.stdout)
        commit_files = {
            file_entry["filename"]
            for file_entry in files_json
            if "filename" in file_entry
        }

        for filepath in commit_files:
            filename = os.path.basename(filepath)
            match = re.match(RECIPE_PATTERN, filename)
            if match:
                suffix = match.group(1) if match.group(1) else ""
                base_name = f"mender{suffix}"
                recipes.append(
                    {
                        "recipe": filename,
                        "base_name": base_name,
                        "major_version": int(match.group(2)),
                    }
                )
    except json.JSONDecodeError:
        print(f"Error: Could not parse API reponse with PR number: {pr_num_from_sha}")
        print(result.stderr)

    return recipes


def test_default_preference(target_branch, master_recipes, commit_recipes):
    """Validates that backported major bumps include DEFAULT_PREFERENCE = '-1'."""

    if target_branch not in ["scarthgap", "wrynose"]:
        pytest.skip(
            f"Skipping check: Target branch is not a maintenance branch (scarthgap / wrynose)"
        )

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
                    "--",
                    f"*{filename}",
                ]
                grep_result = subprocess.run(
                    grep_cmd, cwd=REPO_DIR, capture_output=False, check=False
                )

                if grep_result.returncode != 0:
                    failed_recipes.append(filename)

    assert not failed_recipes, (
        f"The following backported recipes are missing "
        f'DEFAULT_PREFERENCE = "-1": {failed_recipes}'
    )
