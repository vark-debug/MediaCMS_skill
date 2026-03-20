#!/usr/bin/env python3
"""
MediaCMS 分类查询脚本

输出所有可用分类，包含名称、视频数量、浏览链接。

用法:
    python list_categories.py
    python list_categories.py --format json

环境变量:
    VIDEO_API_BASE_URL      服务器地址，例如 https://example.com
    VIDEO_API_USERNAME      用户名
    VIDEO_API_PASSWORD      密码
"""
import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mediacms_client as mc


def list_categories(token):
    """返回所有分类列表（list of dict）"""
    status, data = mc.api_request("GET", "/categories", token=token)
    if status != 200:
        print(f"获取分类失败 [{status}]: {data}")
        return []
    return data if isinstance(data, list) else data.get("results", [])


def category_url(uid):
    """构建分类页面链接"""
    return f"{mc.BASE_URL}/search?category={uid}"


def print_table(categories):
    """以表格形式打印分类列表"""
    col_title = 28
    col_count = 6
    print(f"\n{'='*72}")
    print(f"  {'分类名称':<{col_title}} {'视频数':>{col_count}}  浏览链接")
    print(f"  {'-'*col_title} {'-'*col_count}  {'-'*30}")
    for cat in categories:
        title = cat.get("title", "未命名")
        uid   = cat.get("uid", "")
        count = cat.get("media_count", 0)
        url   = category_url(uid)
        print(f"  {title:<{col_title}} {count:>{col_count}}  {url}")
    print(f"{'='*72}")
    print(f"  共 {len(categories)} 个分类\n")


def print_json(categories):
    """以 JSON 格式输出分类列表"""
    output = [
        {
            "title":       cat.get("title"),
            "uid":         cat.get("uid"),
            "media_count": cat.get("media_count", 0),
            "url":         category_url(cat.get("uid", "")),
        }
        for cat in categories
    ]
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="列出 MediaCMS 所有分类及其链接")
    parser.add_argument(
        "--format", choices=["table", "json"], default="table",
        help="输出格式（默认: table）",
    )
    args = parser.parse_args()

    try:
        mc.check_env()
    except RuntimeError as e:
        print(f"错误：{e}")
        sys.exit(1)

    token = mc.login()
    if not token:
        print("登录失败，请检查用户名和密码")
        sys.exit(1)

    categories = list_categories(token)
    if not categories:
        print("没有可用分类")
        sys.exit(0)

    if args.format == "json":
        print_json(categories)
    else:
        print_table(categories)


if __name__ == "__main__":
    main()
