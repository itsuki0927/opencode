#!/usr/bin/env python3
"""
TCE 发布流水线推进脚本
调用 /deploy/v2/step_check_jump 接口推进流水线到下一阶段

注意：id 参数是质检任务 ID（从 guard_info 接口获取），不是 TCE 工单号
"""

import sys
import json
import ssl
import urllib.request
import urllib.error

# 创建不验证证书的 SSL 上下文（用于内部环境）
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def step_check_jump(guard_id: str, jump_scene: str = "skill_nextstep", reason: str = "运行超过15分钟，无warning/fail") -> bool:
    """
    调用 step_check_jump 接口推进流水线

    Args:
        guard_id: 质检任务 ID（从 guard_info 接口获取的 id 字段）
        jump_scene: 跳转场景
        reason: 跳转原因

    Returns:
        是否成功
    """
    url = "https://crcc.bytedance.net/deploy/v2/step_check_jump"

    data = {
        "id": guard_id,
        "channel": "tce",
        "jumpScene": jump_scene,
        "jumpCustomReason": reason
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))

            if result.get('code') == 0:
                print(f"✅ 已结束流水线的质检环节，推进发布流程到下一阶段")
                return True
            else:
                print(f"❌ 推进失败: {result.get('message', '未知错误')}")
                return False

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP 错误: {e.code} - {e.reason}")
        try:
            error_body = json.loads(e.read().decode('utf-8'))
            print(f"   错误详情: {error_body.get('message', '无详细信息')}")
        except:
            pass
        return False

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("用法: python step_check_jump.py <guard_id> [jump_scene] [reason]")
        print("")
        print("注意：guard_id 是质检任务 ID，从 guard_info 接口获取")
        print("     不是 TCE 工单号！")
        sys.exit(1)

    guard_id = sys.argv[1]
    jump_scene = sys.argv[2] if len(sys.argv) > 2 else "skill_nextstep"
    reason = sys.argv[3] if len(sys.argv) > 3 else "运行超过15分钟，无warning/fail"

    success = step_check_jump(guard_id, jump_scene, reason)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
