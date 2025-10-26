#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度网盘签到脚本
cron: 0 9 * * *
new Env('百度网盘');
"""

import requests
import time
import re
import os
import json
import sys
from datetime import datetime

def send_notification(title, content):
    """发送通知"""
    try:
        sys.path.append('/ql/scripts')
        from sendNotify import send
        send(title, content)
    except ImportError:
        print(f"📢 {title}\n{content}")
    except Exception as e:
        print(f"发送通知失败: {e}")

def log(message, level="INFO"):
    """格式化日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def get_env_config():
    """获取环境变量配置"""
    cookies = os.environ.get('BAIDU_COOKIE', '')
    if not cookies:
        log("❌ 未找到 BAIDU_COOKIE 环境变量", "ERROR")
        return []
    
    cookie_list = [cookie.strip() for cookie in cookies.split('@') if cookie.strip()]
    log(f"📋 共找到 {len(cookie_list)} 个账号配置")
    return cookie_list

class BaiduPanSignin:
    def __init__(self, cookie, account_name=""):
        self.cookie = cookie
        self.account_name = account_name or "账号"
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://pan.baidu.com/wap/svip/growth/task',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': self.cookie
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def signin(self):
        """签到功能"""
        try:
            url = 'https://pan.baidu.com/rest/2.0/membership/level?app_id=250528&web=5&method=signin'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                sign_point = re.search(r'points":(\d+)', response.text)
                signin_error_msg = re.search(r'"error_msg":"(.*?)"', response.text)
                
                if sign_point:
                    points = sign_point.group(1)
                    log(f"✅ {self.account_name} 签到成功，获得积分: {points}")
                    return f"签到成功，获得积分: {points}"
                elif signin_error_msg:
                    error_msg = signin_error_msg.group(1)
                    log(f"⚠️ {self.account_name} 签到信息: {error_msg}")
                    return f"签到信息: {error_msg}"
                else:
                    log(f"✅ {self.account_name} 签到完成")
                    return "签到完成"
            else:
                log(f"❌ {self.account_name} 签到失败，状态码: {response.status_code}", "ERROR")
                return f"签到失败，状态码: {response.status_code}"
                
        except Exception as e:
            log(f"❌ {self.account_name} 签到异常: {str(e)}", "ERROR")
            return f"签到异常: {str(e)}"

    def get_daily_question(self):
        """获取每日答题"""
        try:
            url = 'https://pan.baidu.com/act/v2/membergrowv2/getdailyquestion?app_id=250528&web=5'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                answer = re.search(r'"answer":(\d+)', response.text)
                ask_id = re.search(r'"ask_id":(\d+)', response.text)
                
                if answer and ask_id:
                    return answer.group(1), ask_id.group(1)
                    
        except Exception as e:
            log(f"❌ {self.account_name} 获取每日答题异常: {str(e)}", "ERROR")
            
        return None, None

    def answer_question(self, answer, ask_id):
        """答题功能"""
        try:
            url = f'https://pan.baidu.com/act/v2/membergrowv2/answerquestion?app_id=250528&web=5&ask_id={ask_id}&answer={answer}'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                answer_msg = re.search(r'"show_msg":"(.*?)"', response.text)
                answer_score = re.search(r'"score":(\d+)', response.text)
                
                if answer_score:
                    score = answer_score.group(1)
                    log(f"✅ {self.account_name} 答题成功，获得积分: {score}")
                    return f"答题成功，获得积分: {score}"
                elif answer_msg:
                    msg = answer_msg.group(1)
                    log(f"⚠️ {self.account_name} 答题信息: {msg}")
                    return f"答题信息: {msg}"
                else:
                    log(f"✅ {self.account_name} 答题完成")
                    return "答题完成"
            else:
                log(f"❌ {self.account_name} 答题失败，状态码: {response.status_code}", "ERROR")
                return f"答题失败，状态码: {response.status_code}"
                
        except Exception as e:
            log(f"❌ {self.account_name} 答题异常: {str(e)}", "ERROR")
            return f"答题异常: {str(e)}"

    def get_user_info(self):
        """获取用户信息"""
        try:
            url = 'https://pan.baidu.com/rest/2.0/membership/user?app_id=250528&web=5&method=query'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                current_value = re.search(r'current_value":(\d+)', response.text)
                current_level = re.search(r'current_level":(\d+)', response.text)
                
                level = current_level.group(1) if current_level else '未知'
                value = current_value.group(1) if current_value else '未知'
                
                log(f"📊 {self.account_name} 当前会员等级: {level}，成长值: {value}")
                return f"会员等级: {level}，成长值: {value}"
            else:
                log(f"❌ {self.account_name} 获取用户信息失败，状态码: {response.status_code}", "ERROR")
                return f"获取用户信息失败，状态码: {response.status_code}"
                
        except Exception as e:
            log(f"❌ {self.account_name} 获取用户信息异常: {str(e)}", "ERROR")
            return f"获取用户信息异常: {str(e)}"

    def run_tasks(self):
        """执行所有任务"""
        log(f"🚀 开始执行 {self.account_name} 的任务")
        results = []
        
        signin_result = self.signin()
        results.append(f"📝 签到: {signin_result}")
        
        time.sleep(3)
        
        answer, ask_id = self.get_daily_question()
        if answer and ask_id:
            answer_result = self.answer_question(answer, ask_id)
            results.append(f"🎯 答题: {answer_result}")
        else:
            log(f"⚠️ {self.account_name} 未获取到答题信息")
            results.append("🎯 答题: 未获取到答题信息")
        
        time.sleep(2)
        
        user_info = self.get_user_info()
        results.append(f"👤 用户信息: {user_info}")
        
        return results

def main():
    """主函数"""
    log("🎉 百度网盘签到脚本启动")
    
    cookie_list = get_env_config()
    if not cookie_list:
        log("❌ 未找到有效的Cookie配置，请检查环境变量 BAIDU_COOKIE", "ERROR")
        return
    
    all_results = []
    
    for i, cookie in enumerate(cookie_list, 1):
        account_name = f"账号{i}" if len(cookie_list) > 1 else "账号"
        
        try:
            baidu = BaiduPanSignin(cookie, account_name)
            
            results = baidu.run_tasks()
            all_results.extend([f"\n🔸 {account_name}:"] + results)
            
            if i < len(cookie_list):
                time.sleep(5)
                
        except Exception as e:
            error_msg = f"❌ {account_name} 执行失败: {str(e)}"
            log(error_msg, "ERROR")
            all_results.append(error_msg)
    
    summary = "\n".join(all_results)
    log("📋 所有任务执行完成")
    if os.environ.get('SEND_NOTIFICATION', 'true').lower() in ['true', '1', 'yes']:
        send_notification("百度网盘签到结果", summary)
    
    log("🎉 脚本执行完成")

if __name__ == "__main__":
    main()
