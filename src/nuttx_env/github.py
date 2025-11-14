"""
Utils for work with github
"""

from urllib.parse import urlparse
from dataclasses import dataclass

import requests


GITHUB_API_URL = "https://api.github.com"


# --- Models ---

@dataclass
class GitHubTag:
    """
    Not all fields
    """
    name: str


# --- Methods ---

def gh_parse_url(repo_url: str) -> tuple[str, str]:
    """
    Parse GitHub repository URL and extract owner and repo name

    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        ValueError: If URL is not a valid GitHub repository URL
    """
    parsed = urlparse(repo_url)

    if parsed.netloc not in ['github.com', 'www.github.com']:
        raise ValueError("URL must be a GitHub repository")

    path_parts = parsed.path.strip('/').split('/')
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL format")

    owner = path_parts[0]
    repo_name = path_parts[1]

    return owner, repo_name


def get_github_tags(owner: str, repo: str) -> list[GitHubTag]:
    """
    Fetch all tags from a GitHub repository

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        List of tag information dictionaries

    Raises:
        requests.RequestException: If API request fails
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/tags"

    # TODO: Don't get all, add pages
    response = requests.get(url)
    response.raise_for_status()

    result = []
    for item in response.json():
        result.append(GitHubTag(name=item["name"]))

    return result
