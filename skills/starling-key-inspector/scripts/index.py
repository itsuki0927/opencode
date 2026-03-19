import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import re
from datetime import datetime

# 配置文件路径：~/.neeko-starling-config.json
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".neeko-starling-config.json")

# 定义发布状态映射
DISTRIBUTE_STATUS_MAP = {
    0: "未知",
    1: "仅全量发布",
    2: "仅灰度发布",
    3: "全量+灰度发布",
    4: "仅测试发布",
    5: "全量+测试发布",
    6: "灰度+测试发布",
    7: "全量+灰度+测试发布",
    8: "未发布",
}


def load_config():
    """读取用户全局配置文件"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def find_project_config():
    """
    向上查找 starling.config.js / .cjs 并解析 projectId, namespace, accessKey, secretKey。
    返回: {'projectId': int, 'namespaceIds': [int], 'accessKey': str, 'secretKey': str, 'path': str} 或 None
    """
    curr = os.getcwd()
    while True:
        candidates = [
            os.path.join(curr, "starling.config.js"),
            os.path.join(curr, "starling.config.cjs"),
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                    config = {"path": path}

                    # Regex 匹配 projectId: '123' 或 123
                    pid_match = re.search(r"projectId\s*:\s*['\"]?(\d+)['\"]?", content)
                    if pid_match:
                        config["projectId"] = int(pid_match.group(1))

                    # Regex 匹配 namespace: [1,2] 或 1
                    ns_list_match = re.search(
                        r"namespace\s*:\s*\[([\d\s,]+)\]", content
                    )
                    ns_single_match = re.search(
                        r"namespace\s*:\s*['\"]?(\d+)['\"]?", content
                    )

                    config["namespaceIds"] = []
                    if ns_list_match:
                        raw_list = ns_list_match.group(1)
                        config["namespaceIds"] = [
                            int(x.strip())
                            for x in raw_list.split(",")
                            if x.strip().isdigit()
                        ]
                    elif ns_single_match:
                        config["namespaceIds"] = [int(ns_single_match.group(1))]

                    # Regex 匹配 accessKey 和 secretKey
                    ak_match = re.search(
                        r"accessKey\s*:\s*['\"]([a-zA-Z0-9]+)['\"]", content
                    )
                    if ak_match:
                        config["accessKey"] = ak_match.group(1)

                    sk_match = re.search(
                        r"secretKey\s*:\s*['\"]([a-zA-Z0-9]+)['\"]", content
                    )
                    if sk_match:
                        config["secretKey"] = sk_match.group(1)

                    # 只要解析到了 projectId，就认为这是一个有效的配置
                    if config.get("projectId"):
                        return config

                except Exception:
                    pass

        parent = os.path.dirname(curr)
        if parent == curr:  # 根目录
            break
        curr = parent
    return None


def save_config(config):
    """保存用户全局配置文件"""
    try:
        current = load_config()
        current.update(config)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def exit_with_json(data, code=0):
    """输出 JSON 并退出"""
    print(json.dumps(data, indent=2, ensure_ascii=False))
    sys.exit(code)


def make_request(url, headers=None):
    """发送 HTTP GET 请求 (使用 urllib)"""
    if headers is None:
        headers = {}

    # 创建一个忽略 SSL 证书验证的上下文
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            if 200 <= response.status < 300:
                data = response.read()
                return json.loads(data)
            else:
                raise Exception(f"HTTP Error: {response.status} {response.reason}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        raise Exception(f"HTTP Error: {e.code} {e.reason} - {err_body}")
    except urllib.error.URLError as e:
        raise Exception(f"Network Error: {e.reason}")


def search_key_in_projects(key_text, access_key, secret_key):
    """在所有有权限的项目中搜索 Key"""
    # 用户确认: 该接口一定返回数组 (List)
    url = f"https://starling.bytedance.net/scan/oncall/checkKey?searchKey={urllib.parse.quote(key_text)}"
    headers = {
        "Content-Type": "application/json",
        "x-starling-accesskey": access_key,
        "x-starling-secretkey": secret_key
    }

    try:
        json_resp = make_request(url, headers)
        if isinstance(json_resp, list):
            return json_resp
        # 如果返回的不是列表，视为异常或无结果
        return []
    except Exception:
        return []


def get_key_detail(project_id, namespace_id, key_text, access_key, secret_key):
    """查询单个 Key 的详情，返回 data 对象或 None"""
    url = f"https://65odft76.fn.bytedance.net/project/namespace/source/detail?projectId={project_id}&namespaceId={namespace_id}&keyText={urllib.parse.quote(key_text)}"
    try:
        data = make_request(
            url,
            {
                "Content-Type": "application/json",
                "x-starling-accesskey": access_key,
                "x-starling-secretkey": secret_key,
                "x-starling-from": "agent-skill-starling-key-inspector",
            },
        )
        # 用户确认: 批量请求返回数组，单个key返回对象
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and data.get("keyText"):
            return data
    except Exception:
        pass
    return None


def main():
    global_config = load_config()
    project_config = find_project_config()

    args = sys.argv[1:]

    key_text = ""
    cli_project_id = None
    cli_namespace_id = None
    save_defaults = False
    json_mode = False

    # 解析 CLI 参数
    cli_ak = None
    cli_sk = None

    for arg in args:
        if arg.startswith("--project-id="):
            try:
                cli_project_id = int(arg.split("=")[1])
            except ValueError:
                pass
        elif arg.startswith("--namespace-id="):
            try:
                cli_namespace_id = int(arg.split("=")[1])
            except ValueError:
                pass
        elif arg.startswith("--access-key="):
            cli_ak = arg.split("=", 1)[1]
        elif arg.startswith("--secret-key="):
            cli_sk = arg.split("=", 1)[1]
        elif arg in ("--save", "--set-default"):
            save_defaults = True
        elif arg == "--json":
            json_mode = True
        elif not arg.startswith("-"):
            if not key_text:
                key_text = arg

    # 确定最终使用的 AK/SK
    # 优先级: CLI > Project Config > Env > Global Config
    access_key = cli_ak
    secret_key = cli_sk

    if not access_key:
        access_key = (
            (project_config.get("accessKey") if project_config else None)
            or os.environ.get("STARLING_ACCESS_KEY")
            or global_config.get("accessKey")
            or ""
        )

    if not secret_key:
        secret_key = (
            (project_config.get("secretKey") if project_config else None)
            or os.environ.get("STARLING_SECRET_KEY")
            or global_config.get("secretKey")
            or ""
        )

    if not key_text:
        msg = "Error: Please provide a key text."
        if json_mode:
            exit_with_json({"error": msg}, 1)
        print(msg, file=sys.stderr)
        print(
            "Usage: bash run <key_text> [--project-id=<id>] [--namespace-id=<id>] [--save] [--json]",
            file=sys.stderr,
        )
        sys.exit(1)

    if not access_key or not secret_key:
        msg = "Error: Missing Starling credentials."
        if json_mode:
            exit_with_json({"error": msg, "code": "MISSING_CREDENTIALS"}, 1)
        print(msg, file=sys.stderr)
        print(
            "Please provide --access-key and --secret-key arguments, set STARLING_ACCESS_KEY and STARLING_SECRET_KEY environment variables, or run with --save to persist them.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 确定最终使用的 IDs
    # 逻辑：CLI > Project Config > Global Config
    final_project_id = None
    final_namespace_ids = []

    if cli_project_id:
        final_project_id = cli_project_id
    elif project_config:
        final_project_id = project_config["projectId"]
        if not json_mode:
            print(f"[INFO] Using project config from: {project_config['path']}")
    else:
        final_project_id = global_config.get("projectId")

    if cli_namespace_id:
        final_namespace_ids = [cli_namespace_id]
    elif (
        project_config and not cli_project_id
    ):  # 只有当 project_id 也是从 config 读的（或者被 config 匹配）时才用 config 的 namespace
        final_namespace_ids = project_config["namespaceIds"]
    elif not cli_namespace_id and global_config.get("namespaceId"):
        final_namespace_ids = [global_config.get("namespaceId")]

    data = None
    target_namespace_id = None  # 最终成功获取数据的那个 ID

    # 场景 1: 如果有明确的 Project 和 Namespace 范围，在这些范围里尝试获取
    if final_project_id and final_namespace_ids:
        # 如果有多个 Namespace，依次尝试
        for ns_id in final_namespace_ids:
            # if not json_mode:
            #     print(f"Checking in Project {final_project_id}, Namespace {ns_id}...")
            data = get_key_detail(
                final_project_id, ns_id, key_text, access_key, secret_key
            )
            if data:
                target_namespace_id = ns_id
                break

        # 如果指定了范围但都没找到，data 依然是 None，后面会 fall through 到报错或搜索逻辑（如果允许的话）
        # 但通常如果有 ID，就认为已经定位了。如果没找到，就是 Key 不在这个 Project/Namespace 下。
        if not data and not json_mode:
            print(
                f'[WARN] Key "{key_text}" not found in Project {final_project_id} with Namespaces {final_namespace_ids}.'
            )
            # 这里可以选择是否退化为全范围搜索。目前的逻辑是 Fail。
            # 为了更智能，如果配置错了，可以退化为全范围搜索吗？
            # 暂时保持 Fail，因为配置通常是权威的。

    # 场景 2: 如果没有 ID (或者上面没找到且我们想自动搜)，执行全范围搜索
    if not data:
        # 如果之前尝试了特定 ID 但没找到，打印提示并继续搜索
        if final_project_id and final_namespace_ids:
            if not json_mode:
                print(
                    f'[WARN] Key "{key_text}" not found in the configured Project {final_project_id}. Falling back to search in all accessible projects...',
                    file=sys.stderr,
                )
            # 重置 ID，以便下面进入搜索逻辑
            final_project_id = None
            target_namespace_id = None

        search_key = key_text
        is_batch = "," in key_text

        if is_batch:
            # 如果是批量查询，提取第一个 Key 进行全范围搜索以定位项目上下文
            search_key = key_text.split(",")[0].strip()
            if not json_mode:
                print(
                    f'[INFO] Batch query detected. Searching for context using the first key "{search_key}"...',
                    file=sys.stderr,
                )

        if not json_mode and not is_batch:
            print(
                f'[INFO] Searching for key "{key_text}" in all accessible projects...',
                file=sys.stderr,
            )

        search_results = search_key_in_projects(search_key, access_key, secret_key)

        if len(search_results) == 0:
            if json_mode:
                exit_with_json(
                    {"error": "Key not found in any project", "code": "KEY_NOT_FOUND"},
                    1,
                )
            print(
                f'[ERROR] Key "{search_key}" not found in any accessible project.',
                file=sys.stderr,
            )
            sys.exit(1)
        elif len(search_results) == 1:
            match = search_results[0]
            final_project_id = int(match["projectId"])
            target_namespace_id = int(match["namespaceId"])
            if not json_mode:
                print(
                    f"[SUCCESS] Found context in Project: {match.get('projectName', '')} (ID: {final_project_id}), Namespace: {match.get('namespace', '')} (ID: {target_namespace_id})\n"
                )

            # 获取详情 (此时有了 ID，可以安全地发起批量查询)
            # 注意：这里我们使用原始的 key_text (可能包含多个 key) 进行查询
            data = get_key_detail(
                final_project_id, target_namespace_id, key_text, access_key, secret_key
            )

        else:
            # 多个结果
            if is_batch:
                # 批量模式下，如果有多个项目上下文匹配第一个 Key，我们无法确定使用哪一个，必须报错
                if json_mode:
                    exit_with_json(
                        {
                            "error": f"Ambiguous context for first key '{search_key}'. Found in multiple projects.",
                            "code": "AMBIGUOUS_CONTEXT",
                            "candidates": [
                                {
                                    "projectId": item.get("projectId"),
                                    "projectName": item.get("projectName"),
                                    "namespaceId": item.get("namespaceId"),
                                    "namespace": item.get("namespace"),
                                }
                                for item in search_results
                            ],
                        },
                        1,
                    )
                print(
                    f'[ERROR] First key "{search_key}" found in multiple projects. Cannot determine context for batch query.',
                    file=sys.stderr,
                )
                sys.exit(1)

            # 单个 Key 多个结果，JSON 模式返回列表，CLI 模式让人选
            if json_mode:
                exit_with_json(
                    {
                        "error": "Multiple keys found",
                        "code": "MULTIPLE_KEYS_FOUND",
                        "candidates": [
                            {
                                "projectId": item.get("projectId"),
                                "projectName": item.get("projectName"),
                                "namespaceId": item.get("namespaceId"),
                                "namespace": item.get("namespace"),
                            }
                            for item in search_results
                        ],
                    },
                    1,
                )

            print(
                f'[WARN] Found "{key_text}" in {len(search_results)} places. Please specify which one to use:\n'
            )
            print(
                f"{'Project'.ljust(20)} | {'Project ID'.ljust(12)} | {'Namespace'.ljust(20)} | Namespace ID"
            )
            print("-" * 80)
            for item in search_results:
                p_name = str(item.get("projectName", "")).ljust(20)
                p_id = str(item.get("projectId")).ljust(12)
                n_name = str(item.get("namespace", "")).ljust(20)
                n_id = str(item.get("namespaceId"))
                print(f"{p_name} | {p_id} | {n_name} | {n_id}")
            print("\nRe-run with: --project-id=<id> --namespace-id=<id>")
            sys.exit(1)

    # 兜底：如果还是没 data
    if not data:
        msg = "Failed to retrieve key details."
        if json_mode:
            exit_with_json({"error": msg, "code": "RETRIEVE_FAILED"}, 1)
        print(msg)
        sys.exit(1)

    # --- 输出结果 ---

    # 自动保存配置：只要查询成功，且使用了有效的 AK/SK 或 Project/Namespace，就尝试保存
    # 这样下次就可以复用，不需要用户显式加 --save
    # 但我们还是要谨慎：只有当这些信息真的发生了“发现”或者“指定”时才保存。
    # 鉴于这是一个 skill，为了方便后续调用，我们默认开启“成功即保存”的策略。
    
    new_config = {}
    should_save = False

    # 1. 保存 AK/SK (如果当前使用的有效)
    if access_key and access_key != global_config.get("accessKey"):
        new_config["accessKey"] = access_key
        should_save = True
    
    if secret_key and secret_key != global_config.get("secretKey"):
        new_config["secretKey"] = secret_key
        should_save = True

    # 2. 保存 Project/Namespace Context
    # 只有当这两个 ID 是有效的（无论是通过 CLI 指定，还是全范围搜索发现的），都值得保存为默认上下文
    # 除非用户是在临时查别的项目（但 skill 场景下，通常是在一个项目上下文中工作）
    if final_project_id and target_namespace_id:
        if final_project_id != global_config.get("projectId") or target_namespace_id != global_config.get("namespaceId"):
            new_config["projectId"] = final_project_id
            new_config["namespaceId"] = target_namespace_id
            should_save = True

    if should_save:
        save_config(new_config)
        if not json_mode:
            print(f"[INFO] Context and credentials automatically saved to {CONFIG_FILE}", file=sys.stderr)

    # JSON 输出模式
    if json_mode:
        data_list = data if isinstance(data, list) else [data]
        results = []

        for item in data_list:
            target_texts = item.get("targetTexts", [])
            translations = []
            for t in target_texts:
                translations.append(
                    {
                        "lang": t.get("lang"),
                        "status": DISTRIBUTE_STATUS_MAP.get(
                            t.get("distributeStatus"), "Unknown"
                        ),
                        "statusCode": t.get("distributeStatus"),
                        "content": t.get("content"),
                    }
                )

            results.append(
                {
                    "key": item.get("keyText"),
                    "id": item.get("id"),
                    "projectId": final_project_id,
                    "namespaceId": target_namespace_id,
                    "sourceText": item.get("content"),
                    "sourceLang": item.get("lang"),
                    "updatedAt": item.get("updatedAt") or item.get("updateTime"),
                    "translations": translations,
                }
            )

        # 为了保持向后兼容，如果只有一个结果且输入没有逗号（或者结果本来就不是列表），返回对象
        # 这里简单起见：如果 API 返回的是列表，我们就返回列表；如果是对象，返回对象。
        # 但我们前面把 data 统一转成了 data_list。
        # 逻辑：如果原始 data 是 list，返回 list。如果原始 data 是 dict，返回 dict。
        if isinstance(data, list):
            exit_with_json(results, 0)
        else:
            exit_with_json(results[0], 0)

    # 默认人类友好输出模式
    data_list = data if isinstance(data, list) else [data]

    print(f"\nStarling Key Inspector Result ({len(data_list)} keys)\n")

    for idx, item in enumerate(data_list):
        updated_at = item.get("updatedAt") or item.get("updateTime")
        updated_at_str = str(updated_at) if updated_at else "N/A"

        print(f"Key:         {item.get('keyText')}")
        print(f"Source ID:   {item.get('id')}")
        print(f"Source Text: {item.get('content')} ({item.get('lang')})")
        print(f"Updated:     {updated_at_str}")
        print("-" * 40)

        target_texts = item.get("targetTexts", [])
        if target_texts:
            print(f"Translations ({len(target_texts)}):\n")
            print(f"{'Language'.ljust(10)} | {'Status'.ljust(25)} | {'Translation'}")
            print("-" * 80)

            for target in target_texts:
                status_code = target.get("distributeStatus")
                status_str = DISTRIBUTE_STATUS_MAP.get(
                    status_code, f"Unknown({status_code})"
                )

                clean_text = (target.get("content") or "").replace("\n", "\\n")

                print(
                    f"{target.get('lang').ljust(10)} | {status_str.ljust(25)} | {clean_text}"
                )
        else:
            print("[WARN] No translations found.")

        print("\n" + "=" * 80 + "\n") if idx < len(data_list) - 1 else print("\n")


if __name__ == "__main__":
    main()
