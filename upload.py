#!/usr/bin/env python3
"""
MediaCMS 视频上传脚本

用法:
    python upload.py <视频文件路径> <标题> [选项]

选项:
    --description TEXT   视频描述（默认: Uploaded via API）
    --category NAME      上传后自动归入的分类名称

环境变量:
    VIDEO_API_BASE_URL      服务器地址，例如 https://example.com
    VIDEO_API_USERNAME      用户名
    VIDEO_API_PASSWORD      密码
"""
import os
import sys
import json
import argparse
import urllib.request
import urllib.error

# 确保同目录的 mediacms_client 可被导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mediacms_client as mc


def upload_video(video_path, title, description="Uploaded via API", token=None):
    """上传视频文件，返回 API 响应 dict 或 None"""
    if not os.path.exists(video_path):
        print(f"错误：文件不存在 {video_path}")
        return None

    filename = os.path.basename(video_path)
    mime = (
        "video/mp4"
        if filename.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"))
        else "application/octet-stream"
    )

    with open(video_path, "rb") as f:
        file_data = f.read()

    boundary = "----MediaCMSBoundaryXyZ1234"
    body = b"\r\n".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"title\"\r\n\r\n{title}".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\n{description}".encode(),
        (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"media_file\"; "
            f"filename=\"{filename}\"\r\nContent-Type: {mime}\r\n\r\n"
        ).encode() + file_data,
        f"--{boundary}--".encode(),
    ])

    url = f"{mc.BASE_URL}/api/v1/media"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=mc.ssl_ctx, timeout=300) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"上传失败 [{e.code}]: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"上传错误: {e}")
        return None


def find_category_uid(token, category_name):
    """按名称（大小写不敏感）查找分类 uid，返回 uid 字符串或 None"""
    status, data = mc.api_request("GET", "/categories", token=token)
    if status != 200:
        return None
    categories = data if isinstance(data, list) else data.get("results", [])
    key = category_name.lower()
    for cat in categories:
        if cat.get("title", "").lower() == key:
            return cat.get("uid")
    return None


def set_category(token, friendly_token, category_uid):
    """将视频加入指定分类，返回 (success: bool, response: dict)"""
    payload = json.dumps({
        "media_ids": [friendly_token],
        "action": "add_to_category",
        "category_uids": [category_uid],
    }).encode()
    status, data = mc.api_request(
        "POST", "/media/user/bulk_actions",
        data=payload, content_type="application/json", token=token,
    )
    return status == 200, data


def main():
    parser = argparse.ArgumentParser(description="上传视频到 MediaCMS")
    parser.add_argument("video_file", help="视频文件路径")
    parser.add_argument("title", help="视频标题")
    parser.add_argument("--description", default="Uploaded via API", help="视频描述")
    parser.add_argument("--category", default=None, help="目标分类名称")
    args = parser.parse_args()

    try:
        mc.check_env()
    except RuntimeError as e:
        print(f"错误：{e}")
        sys.exit(1)

    print("正在登录...")
    token = mc.login()
    if not token:
        print("登录失败，请检查用户名和密码")
        sys.exit(1)
    print("登录成功\n")

    # 上传视频
    print(f"正在上传: {args.video_file}")
    print(f"标题: {args.title}")
    result = upload_video(args.video_file, args.title, args.description, token=token)
    if not result:
        sys.exit(1)

    friendly_token = result.get("friendly_token") or result.get("id")
    video_url = f"{mc.BASE_URL}/view?m={friendly_token}"
    print(f"\n✅ 上传成功！")
    print(f"   标题     : {result.get('title', args.title)}")
    print(f"   Token    : {friendly_token}")
    print(f"   视频地址 : {video_url}")

    # 设置分类
    if args.category and friendly_token:
        print(f"\n正在查找分类: {args.category}")
        uid = find_category_uid(token, args.category)
        if uid:
            ok, data = set_category(token, friendly_token, uid)
            if ok:
                print(f"✅ 分类设置成功: {args.category}")
            else:
                print(f"⚠️  分类设置失败: {data}")
        else:
            print(f"⚠️  未找到分类 '{args.category}'，已跳过")

    print(f"\n🎉 完成！视频地址: {video_url}")


if __name__ == "__main__":
    main()
