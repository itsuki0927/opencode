import argparse
import json
import time
import requests
import os

BITS_HOST_CN = "https://bits.bytedance.net"
CASE_GEN_STATUS_URI = "/quality/caseScore/openapi/v1/getCaseGenerate"


def check_case_gen_status(case_generate_id: int) -> tuple:
    """
    检查用例生成任务状态
    返回: {"status": str, "progress": int, "message": str}
    """
    url = f"{BITS_HOST_CN}{CASE_GEN_STATUS_URI}"
    try:
        resp = requests.get(url, params={"caseGenerateId": case_generate_id}, timeout=100)
        resp.raise_for_status()
        data = resp.json()
        if "caseGenerate" in data:
            case_id = data["caseGenerate"].get("caseId")
            mind_nodes = data["caseGenerate"].get("mindNodes")
            if case_id > 0:
                return case_id, mind_nodes, True
            else:
                print(f"⏳ 用例生成任务进行中")
                return case_id, mind_nodes, False
        else:
            return None, None, False

    except Exception as e:
        print(f"用例生成状态检查失败: {e}")
        return None, None, False


def get_case_result(case_generate_id: int, devops_id: str):
    """
    检查用例生成任务状态
    """

    for i in range(10):
        case_id, mind_nodes, is_success = check_case_gen_status(case_generate_id)
        time.sleep(60)
        if is_success:
            case_url = f"{BITS_HOST_CN}/devops/{devops_id}/quality/case/caseDetail/{case_id}"
            print(f"✅ 用例生成成功！用例链接: {case_url}")
            return mind_nodes

    print("⚠️ 用例生成任务还未结束，请稍后继续查询")
    return None


def main():
    parser = argparse.ArgumentParser(description="BITS 平台测试用例生成脚本")
    parser.add_argument(
        "--case_generate_id",
        type=int,
        required=True,
        help="用例生成任务ID",
    )

    parser.add_argument(
        "--output_file",
        required=False,
        type=str,
        help="用例结果文件路径，若未提供则不保存用例结果",
    )

    parser.add_argument(
        "--devops_id",
        required=False,
        type=int,
        default=1123716967682,
        help="用例上传到bits平台的devops_id，若用户未提供则使用默认值1123716967682",
    )

    args = parser.parse_args()
    case_generate_id = args.case_generate_id
    case_result = get_case_result(case_generate_id, args.devops_id)
    if args.output_file:
        if case_result:
            with open(args.output_file, "w", encoding="utf-8") as f:
                json.dump(case_result, f, ensure_ascii=False)
            print(f"✅ 用例结果已保存到 {args.output_file}")


if __name__ == "__main__":
    main()
