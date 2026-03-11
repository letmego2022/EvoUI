# utils/auth_scripts.py
import requests
import json

def get_sid() -> str:
    url = "https://clportal.clpsgroup.com.cn/camapi/auth/login/getSid"
    resp = requests.post(url, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"getSid 失败: HTTP {resp.status_code}")
    data = resp.json()
    if data.get("code") != "000":
        raise RuntimeError(f"getSid 失败: {data.get('msg')}")
    return data["data"]   # 例如 5163211141714121510789601


def get_gtams_url():
    sid = get_sid()
    url = f"https://clportal.clpsgroup.com.cn/camapi/auth/login/sso/{sid}"
    payload = {
        "userName": "DL16064",
        "password": "Lewis123!",
        "sid": sid,
        "nw": "1",
        "dt": "1"
    }
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "python-sdmp-helper/1.0"
    }

    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP 错误: {resp.status_code} {resp.text}")

    try:
        data = resp.json()
    except Exception as e:
        raise RuntimeError("返回体不是合法 JSON") from e

    # 1. 取 token
    token = data["data"]["token"]

    # 2. 取 SDMP url
    sdmp_url = None
    for app in data["data"]["clientList"]:
        if app["name"] == "软件开发管理系统":
            sdmp_url = app["url"].strip()
            break
    if not sdmp_url:
        raise RuntimeError("clientList 中未找到‘软件开发管理系统’")

    return sdmp_url

def get_dashboard_sso_url():
    return "http://dashboard.internal/sso?ticket=abc"

# 【关键】函数注册表，字符串 -> 函数对象
URL_GENERATORS = {
    "get_gtams_url": get_gtams_url,
    "get_dashboard_sso_url": get_dashboard_sso_url
}