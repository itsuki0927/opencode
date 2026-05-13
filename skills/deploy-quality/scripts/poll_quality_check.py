#!/usr/bin/env python3
"""
TCE 发布工单质检轮询脚本
轮询 /deploy/tce/guard_info 接口直到 guard_status=finish 或 skipped
"""

import sys
import time
import json
import ssl
import urllib.request
from typing import Dict, Any, Optional

# 创建不验证证书的 SSL 上下文（用于内部环境）
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def fetch_guard_info(deploy_id: str) -> Optional[Dict[str, Any]]:
    """获取质检任务基本信息"""
    url = f"https://deploy-quality.bytedance.net/deploy/tce/guard_info?deploy_id={deploy_id}"

    try:
        with urllib.request.urlopen(url, timeout=30, context=ssl_context) as response:
            data = json.loads(response.read().decode('utf-8'))
            # 接口返回 {"code": 0, "data": {...}, "message": "ok"}
            # 返回 data 字段中的实际数据
            return data.get('data')
    except Exception as e:
        print(f"请求失败: {e}", file=sys.stderr)
        return None


def fetch_guard_detail(guard_id: str) -> Optional[Dict[str, Any]]:
    """获取质检任务详情（异常时查询）"""
    url = f"https://deploy-quality.bytedance.net/deploy/guard_detail?channel=bytecycle&id={guard_id}"

    try:
        with urllib.request.urlopen(url, timeout=30, context=ssl_context) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('code') == 0:
                return data.get('data', [{}])[0]
            return None
    except Exception as e:
        print(f"详情查询失败: {e}", file=sys.stderr)
        return None


def analyze_check_items(check_items: list) -> Dict[str, Any]:
    """分析检测项结果"""
    summary = {
        'total': len(check_items),
        'pass': 0,
        'warning': 0,
        'fail': 0,
        'abnormal_items': []
    }

    for item in check_items:
        result = item.get('result', '')
        if result == 'pass':
            summary['pass'] += 1
        elif result == 'warning':
            summary['warning'] += 1
            summary['abnormal_items'].append(item)
        elif result == 'fail':
            summary['fail'] += 1
            summary['abnormal_items'].append(item)

    return summary


def format_summary(data: Dict[str, Any]) -> str:
    """格式化质检摘要"""
    output = []
    output.append(f"质检任务 ID: {data.get('guard_id', 'N/A')}")
    output.append(f"PSM: {data.get('psm', 'N/A')}")
    output.append(f"阶段: {data.get('stage', 'N/A')}")
    output.append(f"开始时间: {data.get('start_time', 'N/A')}")
    output.append(f"质检状态: {data.get('guard_status', 'N/A')}")
    output.append(f"质检结果: {data.get('guard_result', 'N/A')}")

    return '\n'.join(output)


def format_abnormal_items(items: list) -> str:
    """格式化异常项详情"""
    if not items:
        return ""

    output = []
    output.append(f"\n详细检测项 ({len(items)} 项异常):")

    for idx, item in enumerate(items, 1):
        output.append(f"\n{idx}. [{item.get('type', 'N/A')}] {item.get('desc', 'N/A')}")
        output.append(f"   结果: {item.get('result', 'N/A')}")
        if item.get('report_url'):
            output.append(f"   报告: {item.get('report_url')}")

    output.append("\n排查建议:")
    output.append("1. 点击报告链接查看详细检测结果")
    output.append("2. 根据错误描述定位问题代码或服务")
    output.append("3. 修复后在 TCE 平台手动处理")

    return '\n'.join(output)


def poll_until_finish(deploy_id: str, interval: int = 15, max_attempts: int = 60) -> Optional[Dict[str, Any]]:
    """轮询直到质检完成"""
    print(f"开始轮询 TCE 工单 {deploy_id} 的质检状态...")
    print(f"轮询间隔: {interval}秒, 最大次数: {max_attempts} (最长约15分钟)\n")

    for i in range(1, max_attempts + 1):
        print(f"[{i}/{max_attempts}] 轮询中... {time.strftime('%Y-%m-%d %H:%M:%S')}")

        data = fetch_guard_info(deploy_id)
        if not data:
            print("  获取数据失败，继续重试...")
            if i < max_attempts:
                time.sleep(interval)
            continue

        # 检查工单是否存在
        if not data.get('found', True):
            print(f"\n❌ 工单 {deploy_id} 不存在或无权访问")
            return {'finished': False, 'deploy_id': deploy_id, 'not_found': True}

        guard_status = data.get('guard_status', '')
        guard_result = data.get('guard_result', '')
        guard_id = data.get('guard_id', '')

        print(f"  guard_status = {guard_status}, guard_result = {guard_result}")

        if guard_status in ['finish', 'skipped']:
            if guard_status == 'finish':
                print("  ✅ 质检已完成！\n")
            else:
                print("  ✅ 质检已跳过！\n")
            print("=== 质检状态摘要 ===")
            print(format_summary(data))

            result_info = {
                'finished': True,
                'deploy_id': deploy_id,
                'guard_id': guard_id,
                'guard_result': guard_result,
                'data': data
            }

            # 如果有异常，查询详情
            if guard_result in ['warning', 'fail', 'error']:
                print(f"\n检测到异常结果 '{guard_result}'，查询详细检测项...")
                detail = fetch_guard_detail(guard_id)
                if detail:
                    check_items = detail.get('check_item_info_list', [])
                    summary = analyze_check_items(check_items)
                    print(format_abnormal_items(summary['abnormal_items']))
                    result_info['has_abnormal'] = True
                    result_info['detail'] = detail
                    result_info['summary'] = summary
                else:
                    result_info['has_abnormal'] = True
                    print("\n⚠️ 无法获取详细检测项信息")
            else:
                result_info['has_abnormal'] = False
                print("\n✅ 无异常检测项，可以推进到下一阶段")

            return result_info

        print(f"  未达到完成条件，{interval}秒后重试...")

        if i < max_attempts:
            time.sleep(interval)

    print(f"\n❌ 超时！轮询超过 15 分钟，质检仍未完成")
    return {'finished': False, 'deploy_id': deploy_id}


def main():
    if len(sys.argv) < 2:
        print("用法: python poll_quality_check.py <deploy_id>")
        sys.exit(1)

    deploy_id = sys.argv[1]
    result = poll_until_finish(deploy_id)

    if result and result.get('finished'):
        # 输出 guard_id 供后续使用
        print(f"\n[GUARD_ID]={result.get('guard_id')}")


if __name__ == '__main__':
    main()
