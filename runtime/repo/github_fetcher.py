"""Lightweight public GitHub repository fetcher.

v0.7 scope: fetch basic context via GitHub REST and raw content endpoints.
No authentication, no private repositories, and no git clone.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from runtime.repo.repo_models import RepoContext


class GitHubRepoFetcher:
    """Fetch public GitHub repository context using the Python standard library."""

    api_base_url = "https://api.github.com"
    raw_base_url = "https://raw.githubusercontent.com"
    key_file_names = (
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "Dockerfile",
        "Makefile",
        "README.md",
    )

    def parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Parse https://github.com/{owner}/{repo} into owner and repo."""
        parsed = urlparse(repo_url)
        if parsed.scheme not in ("http", "https") or parsed.netloc != "github.com":
            raise ValueError(
                "repo_url must use the form https://github.com/{owner}/{repo}"
            )

        parts = [part for part in parsed.path.strip("/").split("/") if part]
        if len(parts) < 2:
            raise ValueError(
                "repo_url must include both owner and repo, for example "
                "https://github.com/owner/repo"
            )

        owner = parts[0]
        repo = parts[1].removesuffix(".git")
        if not owner or not repo:
            raise ValueError("repo_url owner and repo must be non-empty")
        return owner, repo

    def fetch(self, repo_url: str) -> RepoContext:
        """Fetch repository metadata, README, root tree, and key files."""
        owner, repo = self.parse_repo_url(repo_url)
        repo_api_url = f"{self.api_base_url}/repos/{owner}/{repo}"
        repo_data = self._request_json(repo_api_url)
        default_branch = repo_data.get("default_branch")
        if not isinstance(default_branch, str) or not default_branch:
            raise RuntimeError(f"GitHub repo response did not include default_branch")

        readme = self._fetch_readme(owner, repo, default_branch)
        file_tree = self._fetch_root_file_tree(owner, repo, default_branch)
        key_files = self._fetch_key_files(owner, repo, default_branch)

        metadata = {
            "owner": owner,
            "description": repo_data.get("description"),
            "stars": repo_data.get("stargazers_count"),
            "language": repo_data.get("language"),
            "forks": repo_data.get("forks_count"),
            "open_issues": repo_data.get("open_issues_count"),
            "license": self._license_name(repo_data.get("license")),
            "html_url": repo_data.get("html_url"),
        }

        return RepoContext(
            repo_name=repo,
            repo_url=repo_url,
            default_branch=default_branch,
            readme=readme,
            file_tree=file_tree,
            key_files=key_files,
            metadata=metadata,
        )

    def _request_json(self, url: str) -> Any:
        response_text = self._request_text(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"GitHub returned invalid JSON for {url}: {exc}") from exc

    def _request_text(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> str:
        request_headers = {
            "User-Agent": "agent-os-github-fetcher/0.7",
        }
        if headers:
            request_headers.update(headers)

        request = Request(url, headers=request_headers)
        try:
            with urlopen(request, timeout=20) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="replace")
        except HTTPError as exc:
            raise RuntimeError(
                f"GitHub request failed for {url}: HTTP {exc.code} {exc.reason}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"GitHub request failed for {url}: {exc.reason}") from exc
        except TimeoutError as exc:
            raise RuntimeError(f"GitHub request timed out for {url}") from exc

    def _try_request_text(self, url: str) -> str | None:
        try:
            return self._request_text(url)
        except RuntimeError:
            return None

    def _fetch_readme(self, owner: str, repo: str, branch: str) -> str | None:
        for filename in ("README.md", "README", "README.rst"):
            content = self._try_request_text(
                f"{self.raw_base_url}/{owner}/{repo}/{branch}/{filename}"
            )
            if content is not None:
                return content
        return None

    def _fetch_root_file_tree(self, owner: str, repo: str, branch: str) -> list[str]:
        contents_url = (
            f"{self.api_base_url}/repos/{owner}/{repo}/contents?ref={branch}"
        )
        contents = self._request_json(contents_url)
        if not isinstance(contents, list):
            raise RuntimeError("GitHub contents response was not a list")
        names: list[str] = []
        for item in contents:
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                names.append(item["name"])
        return names

    def _fetch_key_files(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> dict[str, str]:
        key_files: dict[str, str] = {}
        for filename in self.key_file_names:
            content = self._try_request_text(
                f"{self.raw_base_url}/{owner}/{repo}/{branch}/{filename}"
            )
            if content is not None:
                key_files[filename] = content
        return key_files

    def _license_name(self, license_data: Any) -> str | None:
        if isinstance(license_data, dict):
            name = license_data.get("name")
            if isinstance(name, str):
                return name
        return None
