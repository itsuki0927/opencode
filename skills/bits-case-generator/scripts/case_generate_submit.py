#!/usr/bin/env python3
"""
BITS 平台测试用例生成脚本
通过调用 BITS OpenAPI 异步生成测试用例，返回用例信息和 BITS 平台链接。

使用方式:
    python3 generate_bits_cases.py --main_doc https://xxx.feishu.cn/wiki/xxx --other_docs ["https://xxx.feishu.cn/wiki/xxx", "https://xxx.feishu.cn/wiki/xxx"] --space_id xxx --dir_id xxx --user_name xxx --user_email xxx

详细参数见 SKILL.md
"""

import argparse
import json
import sys

import requests

# BITS 平台 Host
BITS_HOST_CN = "https://bits.bytedance.net"

# API 路径
CASE_GEN_URI = "/quality/caseScore/openapi/v1/caseGen"
PERMISSION_CHECK_URI = "/quality/caseScore/openapi/v1/caseGenerate/getUserPermissionView"
CASE_GEN_STATUS_URI = "/quality/caseScore/openapi/v1/getCaseGenerate"


def gen_bits_case(args: argparse.Namespace):
    # user_email = args.user_email
    username = args.username
    """构建 BITS OpenAPI 请求体"""
    body = {
        "devopsId": args.devops_id,
        "dirId": args.dir_id,
        "prdLink": args.main_doc,
        "userName": username,
        # "userEmail": user_email,
        "sourceType": 1001,
        "callbackUrl": "",
        "isStrictMode": True,
        "userLarkToken": args.access_token,
    }

    # 可选字段：补充文档链接
    if args.other_docs:
        other_doc_list = args.other_docs.split(",")
        body["supplementPrdLinks"] = other_doc_list

    # 可选字段：Meego 信息
    # if args.meego_url:
    #     body["meegoInfo"] = args.meego_url

    print("📤 正在提交用例生成请求到 BITS 平台...")
    api_response = submit_case_generation(body)
    case_generate_id = api_response["generateId"]
    print(f"📝 用例生成任务 ID: {case_generate_id}")
    case_generate_config = {
        "devops_id": args.devops_id,
        "dir_id": args.dir_id,
        "case_generate_id": case_generate_id,
    }
    print(f"📝 用例生成任务配置: {case_generate_config}")
    print(f"⏳ 用例生成任务提交成功，用例生成任务进行中...")

    return case_generate_id


def check_permission(link: str, user_email: str) -> dict:
    """
    检查用户是否有 PRD 解析权限
    返回: {"hasPermission": bool, "authorizedRedirectUrl": str|None}
    """
    url = f"{BITS_HOST_CN}{PERMISSION_CHECK_URI}"
    user_name = user_email.split("@")[0]
    try:
        resp = requests.get(url, params={"userEmail": user_email, "userName": user_name, "Link": link}, timeout=100)

        if resp.status_code == 200:
            data = resp.json()
            return {
                "hasPermission": data.get("hasPermission", False),
                "authorizedRedirectUrl": None,
            }
        elif resp.status_code == 400:
            data = resp.json()
            redirect_url = None
            if data.get("code") == 1007:
                redirect_url = (
                    data.get("detail", {}).get("extra", {}).get("authorizedRedirectUrl")
                )
            return {
                "hasPermission": False,
                "authorizedRedirectUrl": redirect_url,
                "error": data.get("message", "权限校验失败"),
            }
        else:
            return {
                "hasPermission": False,
                "authorizedRedirectUrl": None,
                "error": f"HTTP {resp.status_code}",
            }
    except Exception as e:
        return {
            "hasPermission": False,
            "authorizedRedirectUrl": None,
            "error": str(e),
        }


def submit_case_generation(body: dict) -> dict:
    """
    提交用例生成请求到 BITS 平台
    返回 API 响应
    """
    url = f"{BITS_HOST_CN}{CASE_GEN_URI}"
    headers = {
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=300)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ BITS API 请求失败: HTTP {resp.status_code}")
        print(f"   响应内容: {resp.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="BITS 平台测试用例生成脚本")
    parser.add_argument(
        "--main_doc",
        required=True,
        help="主文档飞书链接，一般为prd链接",
    )
    parser.add_argument(
        "--other_docs",
        required=False,
        help="其他相关文档链接列表（可选），用于辅助生成测试用例。多个文档链接用,分隔",
    )

    parser.add_argument(
        "--username",
        default="Bytester",
        help="用户id或邮箱前缀, 优先从环境变量或已有信息中获取",
    )

    parser.add_argument(
        "--access_token",
        required=True,
        type=str,
        help="用户飞书的access_token",
    )

    parser.add_argument(
        "--devops_id",
        required=False,
        type=int,
        default=1123716967682,
        help="用例上传到bits平台的devops_id，若用户未提供则使用默认值1123716967682",
    )
    parser.add_argument(
        "--dir_id",
        required=False,
        type=int,
        default=1421755,
        help="用例上传到bits平台的目录id，若未提供则使用默认值1421755",
    )

    parser.add_argument(
        "--output_file",
        required=False,
        type=str,
        help="用例结果文件路径，若未提供则不保存用例结果",
    )
    parser.add_argument(
        "--meego_url",
        required=False,
        type=str,
        help="需求的meego链接",
    )

    args = parser.parse_args()

    # 先检查权限
    # link_list = [args.main_doc]
    # if args.other_docs:
    #     link_list.extend(args.other_docs.split(","))
    # for link in link_list:
    #     perm = check_permission(link, args.user_email)
    #     if not perm.get("hasPermission"):
    #         if perm.get("authorizedRedirectUrl"):
    #             print("⚠️ 用户尚未授权 BITS 平台读取飞书文档权限。")
    #             print(f"   请访问以下链接完成授权：")
    #             print(f"   {perm['authorizedRedirectUrl']}")
    #         else:
    #             print(f"⚠️ 权限检查未通过: {link}")
    #             print("   可申请文档权限，或尝试将 PRD 文档分享给「Bits-测试管理」机器人后重试。")
    #
    #         return

    # 构建请求体
    result = gen_bits_case(args)


if __name__ == "__main__":
    main()
