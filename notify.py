#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cron: 20 8 * * *
new Env('V2EX 每日签到');
"""

import requests
import re
import os
import time
import sys

try:
    from notify import send
except ImportError:
    print("未找到 notify.py，将仅在控制台输出日志。")
    def send(title, content):
        pass

def get_headers(cookie):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Cookie": cookie,
        "Referer": "https://www.v2ex.com/",
        "Connection": "keep-alive"
    }

def do_v2ex_tasks(cookie):
    session = requests.Session()
    session.headers.update(get_headers(cookie))
    msg_list = []
    is_success = False # 增加一个状态标识位，记录该账号最终是否成功

    try:
        # --- 1. 访问签到页，检查状态并获取 once 令牌 ---
        daily_url = "https://www.v2ex.com/mission/daily"
        resp1 = session.get(daily_url, timeout=10)
        content1 = resp1.text

        # 检查是否未登录
        if "需要先登录" in content1 or "Sign in" in content1:
            return False, "❌ 登录失效: 请检查 Cookie 是否有效或已过期"

        if "每日登录奖励已领取" in content1:
            msg_list.append("✅ 签到状态: 今日已签到")
            is_success = True
        else:
            once_match = re.search(r'once=([^"\'\s>]+)', content1)
            if not once_match:
                return False, "❌ 签到失败: 未能获取到 once 参数，可能是页面结构改变或账号异常。"
            
            once = once_match.group(1)
            
            # --- 2. 发送签到请求 ---
            redeem_url = f"https://www.v2ex.com/mission/daily/redeem?once={once}"
            session.headers.update({"Referer": daily_url})
            resp2 = session.get(redeem_url, allow_redirects=False, timeout=10)
            
            if resp2.status_code == 302:
                msg_list.append("✅ 签到请求: 发送成功 (HTTP 302)")
                is_success = True
            else:
                msg_list.append(f"⚠️ 签到请求: 状态异常 (HTTP {resp2.status_code})")
                is_success = False
            
            time.sleep(1)

        # --- 3. 获取统计数据 (仅在成功或已签到的情况下才去获取) ---
        if is_success:
            resp3 = session.get(daily_url, timeout=10)
            days_match = re.search(r'已连续登录\s*(.+?)\s*天', resp3.text)
            log_days = days_match.group(1) if days_match else "未知"

            balance_url = "https://www.v2ex.com/balance"
            resp4 = session.get(balance_url, timeout=10)
            reward_match = re.search(r'每日登录奖励\s*(.+?)\s*铜币', resp4.text)
            log_value = reward_match.group(1) if reward_match else "获取失败/无收益"

            msg_list.append(f"🎉 统计: 已连续登录 {log_days} 天 , 每日登录奖励 {log_value} 铜币")

    except Exception as e:
        return False, f"❌ 执行异常: {str(e)}"

    return is_success, "\n".join(msg_list)

def main():
    print("=== 开始执行 V2EX 每日签到任务 ===\n")
    
    cookies = []
    
    env_keys = list(os.environ.keys())
    target_keys = [k for k in env_keys if k.upper().startswith("V2EX_COOKIES")]
    target_keys.sort()

    for key in target_keys:
        env_val = os.environ.get(key)
        if env_val and env_val.strip():
            parsed_cookies = [c.strip() for c in env_val.replace('&', '\n').split('\n') if c.strip()]
            cookies.extend(parsed_cookies)
    
    if not cookies:
        print("\n❌ 致命错误：未获取到任何有效的 Cookie 值，脚本退出。")
        sys.exit(1)

    print(f"共检测到 {len(cookies)} 个账号，准备执行...\n")
    
    final_messages = []
    fail_count = 0 # 记录失败的账号数量
    
    for index, cookie in enumerate(cookies):
        print(f"--- 正在处理第 {index + 1} 个账号 ---")
        
        # 接收状态和日志信息
        success, result_msg = do_v2ex_tasks(cookie)
        print(result_msg)
        final_messages.append(result_msg)
        
        if not success:
            fail_count += 1 # 如果失败，计数器 +1
            
        print("-" * 30 + "\n")
        
        if index < len(cookies) - 1:
            time.sleep(3) 

    send("V2EX 每日签到", "\n\n".join(final_messages))
    
    # 最终状态判定，只要有 1 个及以上账号失败，就抛出异常让面板报红
    if fail_count > 0:
        print(f"\n❌ 任务结束：共有 {fail_count} 个账号执行失败！触发面板报错。")
        sys.exit(1)
    else:
        print("\n=== 🎉 所有账号任务执行完毕 ===")

if __name__ == "__main__":
    main()