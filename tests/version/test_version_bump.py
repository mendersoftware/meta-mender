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
import urllib.request
from pathlib import Path
import pytest

GITHUB_AUTH = os.getenv("GITHUB_AUTH")
CI_COMMIT_SHA = os.getenv("CI_COMMIT_SHA")
RECIPE_PATTERN = r"^mender(-[a-z0-9-]+)?_([0-9]+)\.[0-9]+\.[0-9]+\.bb$"
REPO_DIR = Path(__file__).resolve().parent.parent.parent
YOCTO_BRANCHES = ["scarthgap", "wrynose"]

if not GITHUB_AUTH or not CI_COMMIT_SHA:
    pytest.exit("Missing required environment variables: GITHUB_AUTH or CI_COMMIT_SHA")


def github_api_get(url):
    """Helper to make authenticated GitHub API requests."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "GitLab-CI-Python")
    req.add_header(*GITHUB_AUTH.split(":", 1))

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in [401, 403]:
            pytest.fail(
                f"GitHub API Error ({e.code}) for URL: {url}. "
                f"Your GITHUB_AUTH token header was rejected by GitHub's gateway."
            )
        else:
            print(f"GitHub API Request Failed for {url}: {e}")
            return None
    except Exception as e:
        print(f"GitHub API Request Failed for {url}: {e}")
        return None


@pytest.fixture(scope="session")
def pr_num_from_sha():
    """Returns the pull request number from environment or GitHub Search API."""
    # Pull from GitLab's branch ref name (e.g., 'pr_2449')
    ref_name = os.getenv("CI_COMMIT_REF_NAME", "")
    ref_match = re.match(r"^pr_(\d+)$", ref_name)
    if ref_match:
        return ref_match.group(1)

    # Fallback to Search API
    url = f"https://api.github.com/search/issues?q=repo:mendersoftware/meta-mender+type:pr+sha:{CI_COMMIT_SHA}"
    data = github_api_get(url)

    if data and data.get("items"):
        return str(data["items"][0].get("number", ""))

    pytest.skip(
        f"Commit {CI_COMMIT_SHA} is not yet indexed or associated with a GitHub PR."
    )


@pytest.fixture(scope="session")
def target_branch(pr_num_from_sha):
    """Returns the target branch of the pull request."""
    url = f"https://api.github.com/repos/mendersoftware/meta-mender/pulls/{pr_num_from_sha}"
    data = github_api_get(url)

    if data and "base" in data:
        return data["base"].get("ref")

    pytest.skip(f"Could not retrieve target branch details for PR #{pr_num_from_sha}.")


@pytest.fixture(scope="session")
def target_recipes(target_branch):
    """Gets the target branch recipe data."""
    if target_branch not in YOCTO_BRANCHES:
        pytest.skip(
            "Skipping check: Target branch is not a maintenance branch (scarthgap / wrynose)"
        )

    print(f"Fetching target branch '{target_branch}' from origin...")
    subprocess.run(
        ["git", "fetch", "origin", f"{target_branch}:{target_branch}", "--depth=1"],
        cwd=REPO_DIR,
        check=True,
        capture_output=True,
        text=True,
    )

    cmd = ["git", "ls-tree", "-r", target_branch]

    result = subprocess.run(
        cmd, cwd=REPO_DIR, check=True, capture_output=True, text=True
    )

    # Find and process recipes
    latest_recipes = {}
    for filepath in result.stdout.splitlines():
        if not filepath.endswith(".bb"):
            continue

        filename = os.path.basename(filepath)
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

    # Return a dictionary mapped by filename
    return {
        base_name: item["major_version"] for base_name, item in latest_recipes.items()
    }


@pytest.fixture(scope="session")
def commit_recipes(pr_num_from_sha):
    """Gets the recipes modified or added in the pull request."""
    url = f"https://api.github.com/repos/mendersoftware/meta-mender/pulls/{pr_num_from_sha}/files"
    files_json = github_api_get(url)

    recipes = []
    if not files_json or not isinstance(files_json, list):
        pytest.skip(
            f"Could not retrieve the modified files list for PR #{pr_num_from_sha}."
        )

    commit_files = {
        file_entry["filename"] for file_entry in files_json if "filename" in file_entry
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

    return recipes


def test_default_preference(target_branch, target_recipes, commit_recipes):
    """Validates that backported major bumps include DEFAULT_PREFERENCE = '-1'."""
    if not commit_recipes:
        pytest.skip("No mender recipes found in this commit.")

    failed_recipes = []

    for commit_item in commit_recipes:
        filename = commit_item["recipe"]
        base_name = commit_item["base_name"]
        commit_version = commit_item["major_version"]

        # Check if this exact file existed in target branch
        if base_name in target_recipes:
            target_version = target_recipes[base_name]

            # If the current commit features a higher major version than target branch
            if commit_version > target_version:
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
        "The following backported recipes are missing "
        f'DEFAULT_PREFERENCE = "-1": {failed_recipes}'
    )
