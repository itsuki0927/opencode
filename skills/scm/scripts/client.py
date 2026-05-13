import os
from typing import Any, Dict, List, Optional

import requests


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    return float(raw)


DEFAULT_TIMEOUT_SECONDS = _env_float("SCM_HTTP_TIMEOUT_SECONDS", 10.0)


class HttpError(RuntimeError):
    pass

class ScmClient:
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.base_url = (base_url or os.getenv("SCM_BASE_URL") or "https://scm.byted.org").rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

        effective_token = token if token is not None else os.getenv("SCM_JWT_TOKEN")
        if effective_token:
            self.session.headers.update({"x-jwt-token": effective_token})

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params, timeout=self.timeout_seconds)
        return self._raise_or_json(response)

    def _post(self, path: str, json_data: Dict) -> Any:
        url = f"{self.base_url}{path}"
        response = self.session.post(url, json=json_data, timeout=self.timeout_seconds)
        return self._raise_or_json(response)

    def _patch(self, path: str, json_data: Dict) -> Any:
        url = f"{self.base_url}{path}"
        response = self.session.patch(url, json=json_data, timeout=self.timeout_seconds)
        return self._raise_or_json(response)

    def get_repo_by_id(self, repo_id: int) -> Dict:
        return self._get(f"/api/repos/{repo_id}")

    def get_repo_by_name(self, name: str) -> Dict:
        data = self._get("/api/v2/repos/by_names", params={"repo_names": name})
        if not data:
            raise ValueError(f"Repo with name '{name}' not found")
        return data[0]

    def get_version_by_id(self, version_id: int) -> Dict:
        return self._get(f"/api/v2/versions/{version_id}")

    def get_version_by_number(self, repo_id: int, version_number: str) -> Dict:
        return self._get(f"/api/repos/{repo_id}/versions/{version_number}")

    def get_version_status(self, version_id: int) -> Dict:
        return self._get(f"/api/v2/versions/{version_id}/cicd_poll")

    def get_version_dependencies(self, version_id: int) -> Dict:
        return self._get(f"/api/v2/program_depend/{version_id}/")

    def get_version_list(self, repo_id: int, limit: int = 10) -> List[Dict]:
        data = self._get("/api/v2/versions", params={"repos_id": repo_id, "limit": limit})
        return data.get("results", [])

    def create_version(self, data: Dict) -> Dict:
        resp = self._post("/api/v2/versions/cicd_create/", json_data=data)
        if resp.get("code") != 0:
            raise Exception(f"API Error: {resp.get('error')}")
        if resp.get("data", {}).get("state") != "passed":
            raise Exception(f"Create version failed: {resp.get('data', {}).get('state')}")
        return resp.get("data", {}).get("context")

    def get_config_diff(self, repo_id: int, left: str, right: str) -> Dict:
        resp = self._get(f"/api/v2/repos/{repo_id}/config_diff/", params={"left": left, "right": right})
        if resp.get("code") != 0:
            raise Exception(f"Config diff error: {resp.get('error')}")
        return resp.get("data")

    def get_env_diff(self, repo_id: int, left: str, right: str) -> Dict:
        resp = self._get(f"/api/v2/repos/{repo_id}/env_diff/", params={"left": left, "right": right})
        if resp.get("code") != 0:
            raise Exception(f"Env diff error: {resp.get('error')}")
        return resp.get("data")

    def get_build_env_diff(self, repo_id: int, left: str, right: str) -> Dict:
        resp = self._get(f"/api/v2/repos/{repo_id}/build_env_diff/", params={"left": left, "right": right})
        if resp.get("code") != 0:
            raise Exception(f"Build env diff error: {resp.get('error')}")
        return resp.get("data")

    @staticmethod
    def _raise_or_json(response: requests.Response) -> Any:
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            text = (response.text or "").strip()
            snippet = text[:200] if text else ""
            raise HttpError(f"HTTP {response.status_code} {response.url} {snippet}") from e

        try:
            return response.json()
        except ValueError as e:
            text = (response.text or "").strip()
            snippet = text[:200] if text else ""
            raise HttpError(f"Non-JSON response {response.url} {snippet}") from e


class ByteBuildClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.base_url = (base_url or os.getenv("BYTEBUILD_BASE_URL") or "https://bytebuild-nightly.byted.org").rstrip("/")
        self.timeout_seconds = timeout_seconds

    def get_build_log(self, record_id: int, step_name: str) -> str:
        url = f"{self.base_url}/api/v1/record/logs/{record_id}/{step_name}"
        response = requests.get(url, timeout=self.timeout_seconds)
        if response.status_code != 200:
            raise HttpError(f"HTTP {response.status_code} {url}")
        try:
            return response.json()
        except ValueError:
            return response.text
