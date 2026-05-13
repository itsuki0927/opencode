import base64
import json
from typing import Any, Dict, Optional

try:
    from .client import ScmClient, ByteBuildClient
    from .filters_config import REPO_HIDDEN_KEYS, VERSION_ALWAYS_KEEP_KEYS, VERSION_DROP_KEYS, VERSION_HIDDEN_PREFIXES
except ImportError:
    from client import ScmClient, ByteBuildClient
    from filters_config import REPO_HIDDEN_KEYS, VERSION_ALWAYS_KEEP_KEYS, VERSION_DROP_KEYS, VERSION_HIDDEN_PREFIXES


def _resolve_version_id(version: Dict[str, Any]) -> Optional[int]:
    version_info = version.get("version_info")
    if isinstance(version_info, dict):
        version_id = version_info.get("id")
        if isinstance(version_id, int):
            return version_id
    version_id = version.get("id")
    if isinstance(version_id, int):
        return version_id
    return None


def _b64url_decode(raw: str) -> bytes:
    padded = raw + "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def _decode_jwt_payload(token: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) < 2:
        raise RuntimeError("Invalid SCM_JWT_TOKEN")
    try:
        payload_raw = _b64url_decode(parts[1]).decode("utf-8")
        payload = json.loads(payload_raw)
    except Exception as e:
        raise RuntimeError("Invalid SCM_JWT_TOKEN") from e
    if not isinstance(payload, dict):
        raise RuntimeError("Invalid SCM_JWT_TOKEN")
    return payload


def _resolve_create_user_from_jwt(token: str) -> str:
    payload = _decode_jwt_payload(token)

    candidates = [
        "user_name",
        "username",
        "preferred_username",
        "sub",
        "email",
        "upn",
        "name",
    ]
    for key in candidates:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            v = value.strip()
            if key == "email" and "@" in v:
                v = v.split("@", 1)[0]
            return v
    raise RuntimeError("Could not resolve create_user from SCM_JWT_TOKEN")


def _compact_version_result(version: Dict[str, Any]) -> Dict[str, Any]:
    builds = version.get("builds")
    if not isinstance(builds, list) or not builds:
        return version

    build_keys: set[str] = set()
    for build in builds:
        if isinstance(build, dict):
            build_keys.update(build.keys())

    compacted = dict(version)
    for key in list(compacted.keys()):
        if key in VERSION_HIDDEN_PREFIXES:
            compacted.pop(key, None)
            continue
        for prefix in VERSION_HIDDEN_PREFIXES:
            if key.startswith(f"{prefix}_"):
                compacted.pop(key, None)
                break
    keys = list(compacted.keys())
    for key in keys:
        if key in VERSION_ALWAYS_KEEP_KEYS:
            continue
        if key in build_keys:
            compacted.pop(key, None)
            continue
        for build_key in build_keys:
            if key.startswith(f"{build_key}_"):
                compacted.pop(key, None)
                break
        if key not in compacted:
            continue
        if "_aarch64" in key:
            base = key.replace("_aarch64", "")
            if base in build_keys or base in compacted:
                compacted.pop(key, None)
                continue

    for key in VERSION_DROP_KEYS:
        compacted.pop(key, None)

    return compacted


def _compact_repo_result(repo: Dict[str, Any]) -> Dict[str, Any]:
    compacted = dict(repo)
    for key in REPO_HIDDEN_KEYS:
        compacted.pop(key, None)
    return compacted


class ScmTools:
    def __init__(self):
        self.scm_client = ScmClient()
        self.bytebuild_client = ByteBuildClient()

    def get_repo(self, repo_id: Optional[int] = None, repo_name: Optional[str] = None) -> Dict:
        if repo_id:
            repo = self.scm_client.get_repo_by_id(repo_id)
            if isinstance(repo, dict):
                return _compact_repo_result(repo)
            return repo
        if repo_name:
            repo = self.scm_client.get_repo_by_name(repo_name)
            if isinstance(repo, dict):
                return _compact_repo_result(repo)
            return repo
        raise ValueError("Either repo_id or repo_name must be provided")

    def _resolve_repo(self, repo_id: Optional[int], repo_name: Optional[str]) -> int:
        if repo_id:
            return repo_id
        if repo_name:
            repo = self.scm_client.get_repo_by_name(repo_name)
            return repo['id']
        raise ValueError("Either repo_id or repo_name must be provided")

    def get_version(
        self,
        version_id: Optional[int] = None,
        version_number: Optional[str] = None,
        repo_id: Optional[int] = None,
        repo_name: Optional[str] = None,
    ) -> Dict:
        if version_id:
            version = self.scm_client.get_version_by_id(version_id)
            if isinstance(version, dict):
                return _compact_version_result(version)
            return version
        
        if version_number:
            repo_id = self._resolve_repo(repo_id, repo_name)
            version = self.scm_client.get_version_by_number(repo_id, version_number)
            if isinstance(version, dict):
                return _compact_version_result(version)
            return version
            
        raise ValueError("Either version_id or version_number must be provided")

    def get_version_status(
        self,
        version_id: Optional[int] = None,
        version_number: Optional[str] = None,
        repo_id: Optional[int] = None,
        repo_name: Optional[str] = None,
    ) -> Dict:
        if version_number:
            version = self.get_version(version_number=version_number, repo_id=repo_id, repo_name=repo_name)
            version_id = _resolve_version_id(version)

        if not version_id:
            raise ValueError("Could not resolve version_id")

        return self.scm_client.get_version_status(version_id)

    def get_version_dependencies(
        self,
        version_id: Optional[int] = None,
        version_number: Optional[str] = None,
        repo_id: Optional[int] = None,
        repo_name: Optional[str] = None,
    ) -> Dict:
        if version_number:
            version = self.get_version(version_number=version_number, repo_id=repo_id, repo_name=repo_name)
            version_id = _resolve_version_id(version)

        if not version_id:
            raise ValueError("Could not resolve version_id")

        return self.scm_client.get_version_dependencies(version_id)

    def get_version_list(self, repo_id: Optional[int] = None, repo_name: Optional[str] = None, limit: int = 10) -> list:
        repo_id = self._resolve_repo(repo_id, repo_name)
        return self.scm_client.get_version_list(repo_id, limit)

    def create_version(
        self,
        repo_id: Optional[int] = None,
        repo_name: Optional[str] = None,
        type: str = "online",
        pub_base: str = "branch_base",
        branch_name: Optional[str] = None,
        commit_hash: Optional[str] = None,
        build_image: Optional[str] = None,
    ) -> Dict:
        resolved_repo_id = self._resolve_repo(repo_id, repo_name)

        if pub_base == "branch_base" and not branch_name:
            raise ValueError("branch_name is required when pub_base=branch_base")
        if pub_base == "commit_base" and not commit_hash:
            raise ValueError("commit_hash is required when pub_base=commit_base")

        authed_client = ScmClient()
        if "x-jwt-token" not in authed_client.session.headers:
            raise RuntimeError("Missing SCM_JWT_TOKEN")
        token = authed_client.session.headers.get("x-jwt-token")
        if not isinstance(token, str) or not token.strip():
            raise RuntimeError("Missing SCM_JWT_TOKEN")
        create_user = _resolve_create_user_from_jwt(token)

        data = {
            "repo_id": resolved_repo_id,
            "type": type,
            "pub_base": pub_base,
            "create_user": create_user,
        }
        if branch_name:
            data["branch_name"] = branch_name
        if commit_hash:
            data["commit_hash"] = commit_hash
        if build_image:
            data["build_image"] = build_image
            
        return authed_client.create_version(data)

    def get_version_diff(self, left_version_number: str,
                        right_version_number: str,
                        repo_id: Optional[int] = None,
                        repo_name: Optional[str] = None) -> Dict:
        if "x-jwt-token" not in self.scm_client.session.headers:
            raise RuntimeError("Missing SCM_JWT_TOKEN")
        
        repo_id = self._resolve_repo(repo_id, repo_name)
        
        left_ver = self.scm_client.get_version_by_number(repo_id, left_version_number)
        right_ver = self.scm_client.get_version_by_number(repo_id, right_version_number)
        
        if not left_ver:
            raise ValueError(f"Left version {left_version_number} not found")
        if not right_ver:
            raise ValueError(f"Right version {right_version_number} not found")
             
        left_id = _resolve_version_id(left_ver)
        right_id = _resolve_version_id(right_ver)

        if left_id and right_id and right_id <= left_id:
            raise ValueError(f"Invalid version order: right version must be newer than left version")

        return {
            "config_diff": self.scm_client.get_config_diff(repo_id, left_version_number, right_version_number),
            "env_diff": self.scm_client.get_env_diff(repo_id, left_version_number, right_version_number),
            "build_env_diff": self.scm_client.get_build_env_diff(repo_id, left_version_number, right_version_number)
        }

    def get_build_log(
        self,
        version_number: str,
        repo_id: Optional[int] = None,
        repo_name: Optional[str] = None,
        step_name: str = "building",
        arch: str = "x86_64",
    ) -> Any:
        
        repo_id = self._resolve_repo(repo_id, repo_name)
        version = self.scm_client.get_version_by_number(repo_id, version_number)
        
        if not version:
            raise ValueError(f"Version {version_number} not found")

        build_info_map = version.get('build_info', {})
        
        target_build = build_info_map.get(arch)
        if not target_build:
            raise ValueError(f"No build info found for arch {arch}")
            
        build_num = target_build.get('build_num')
        if not build_num:
            raise ValueError(f"No build number found for arch {arch}")

        return self.bytebuild_client.get_build_log(build_num, step_name)
