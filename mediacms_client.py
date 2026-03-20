#!/usr/bin/env python3
"""
MediaCMS API 公共客户端模块

环境变量：
    VIDEO_API_BASE_URL      服务器地址，例如 https://example.com
    VIDEO_API_USERNAME      用户名
    VIDEO_API_PASSWORD      密码
"""
import os
import base64
import json
import ssl
import urllib.request
import urllib.parse
import urllib.error

# ==================== 配置（从环境变量读取）====================
BASE_URL = os.environ.get("VIDEO_API_BASE_URL", "").rstrip("/")
USERNAME = os.environ.get("VIDEO_API_USERNAME", "")
PASSWORD = os.environ.get("VIDEO_API_PASSWORD", "")

# 忽略 SSL 证书验证（用于自签名证书服务器）
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def check_env():
    """检查必要环境变量，未配置时抛出 RuntimeError"""
    missing = []
    if not BASE_URL:
        missing.append("VIDEO_API_BASE_URL")
    if not USERNAME:
        missing.append("VIDEO_API_USERNAME")
    if not PASSWORD:
        missing.append("VIDEO_API_PASSWORD")
    if missing:
        raise RuntimeError(f"未设置环境变量: {', '.join(missing)}")


def login(username=None, password=None):
    """
    登录获取 Token。

    返回 token 字符串，失败返回 None。
    """
    u = username or USERNAME
    p = password or PASSWORD
    url = f"{BASE_URL}/api/v1/login"
    data = urllib.parse.urlencode({"username": u, "password": p}).encode()
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result.get("token")
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"登录失败 [{e.code}]: {body}")
        return None
    except Exception as e:
        print(f"登录请求错误: {e}")
        return None


def api_request(method, path, data=None, content_type=None, token=None, timeout=60):
    """
    发送 MediaCMS API 请求。

    参数：
        method       : HTTP 方法，例如 "GET" / "POST" / "PUT"
        path         : API 路径，例如 "/categories"
        data         : bytes 请求体（POST/PUT 时使用）
        content_type : Content-Type 请求头
        token        : 登录后获得的 Token
        timeout      : 超时秒数

    返回 (status_code: int, response: dict)
    """
    url = f"{BASE_URL}/api/v1{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Token {token}"
    if content_type:
        headers["Content-Type"] = content_type

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return e.code, {"error": body}
    except Exception as e:
        return 0, {"error": str(e)}
