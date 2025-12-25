# 微信小程序：乐爽洗衣
# 环境变量：lsxy，值authorization_bar，多账号@或换行
# 签到，看视频，可以兑换余额，免费洗衣服
import requests
import time
import os
from datetime import datetime
import random

BASE_URL = "https://nad.ehuoke.com/gw/advert/mini-program/ext"

API = {
    "task_list":    f"{BASE_URL}/daily-task/common/task-list/LS",
    "sign_week":    f"{BASE_URL}/sign-in/one-week-data?equipmentTypeValue=LS",
    "sign_do":      f"{BASE_URL}/sign-in/save",
    "balance":      f"{BASE_URL}/benefit/common/user-benefit/LS",
    "task_receive": f"{BASE_URL}/daily-task/common/receive/LS",
}

def get_tokens():
    raw = os.getenv("lsxy")
    if not raw:
        print("未检测到 lsxy 环境变量")
        return []
    tokens = [t.strip() for t in raw.replace("\n", "@").split("@") if t.strip()]
    print(f"加载 {len(tokens)} 个账号")
    return tokens

def make_session(token):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 MicroMessenger/7.0.20.1781 MiniProgramEnv/Windows WindowsWechat XWEB/16467",
        'xweb_xhr': "1",
        'content-type': "application/json",
        'authorization_bar': token,
        'referer': "https://servicewechat.com/wx99f616aae965882c/33/page-frame.html",
    }
    s = requests.Session()
    s.headers.update(headers)
    return s

def get_balance(s):
    return s.get(API["balance"]).json().get("body", 0)

def get_task_list(s):
    return s.get(API["task_list"]).json().get("body", [])

def need_sign_today(s):
    data = s.get(API["sign_week"]).json().get("body", [])
    today = datetime.now().strftime("%Y-%m-%d")
    for item in data:
        if item["date"] == today:
            return not item["sign"], item.get("reward", 0)
    return True, 10

def do_sign(s):
    return s.post(API["sign_do"], json={"equipmentTypeValue": "LS"}).json().get("code") == "0000000"

def do_task(s, task_id):
    return s.post(API["task_receive"], json={"taskId": task_id}).json().get("code") == "0000000"

def run_account(token, idx):
    s = make_session(token)
    print(f"第 {idx} 个账号开始")

    old = get_balance(s)
    print(f"当前余额：{old}")

    can_sign, reward = need_sign_today(s)
    if can_sign:
        if do_sign(s):
            print(f"签到成功 +{reward}")
        else:
            print("签到失败")
    else:
        print("已签到")

    tasks = [t for t in get_task_list(s) 
             if t["name"] == "浏览15秒视频" and t["taskCompleteTimes"] < t["taskTimes"]]

    print(f"发现 {len(tasks)} 个视频任务")

    ok = 0
    for i, task in enumerate(tasks, 1):
        if do_task(s, task["id"]):
            ok += 1
            print(f"  {i}/{len(tasks)} 完成 +20")
        else:
            print(f"  {i} 失败")

        if i < len(tasks):
            delay = round(random.uniform(15.0, 20.0), 2)
            print(f"  等待 {delay}s")
            time.sleep(delay)

    new = get_balance(s)
    earn = new - old
    print(f"本次获得 {earn} ，当前余额 {new}\n")

def main():
    for i, tk in enumerate(get_tokens(), 1):
        try:
            run_account(tk, i)
        except Exception as e:
            print(f"第 {i} 个账号错误：{e}\n")
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    main()