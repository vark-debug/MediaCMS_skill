#!/usr/bin/env python3
"""
MediaCMS 视频标题 / 分类修改脚本

用法:
    # 通过 friendly_token 修改标题
    python update_category.py <token> --title "新标题"

    # 通过 friendly_token 替换分类（移除旧分类 + 添加新分类）
    python update_category.py <token> --category "新分类名"

    # 同时修改标题和分类
    python update_category.py <token> --title "新标题" --category "新分类"

    # 通过关键词搜索视频后修改
    python update_category.py --search "视频标题关键词" --title "新标题"

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
import urllib.parse
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mediacms_client as mc


def get_categories(token):
    """返回分类列表"""
    status, data = mc.api_request("GET", "/categories", token=token)
    if status != 200:
        return []
    return data if isinstance(data, list) else data.get("results", [])


def find_category_uid(categories, name):
    """按名称（大小写不敏感）查找分类 uid"""
    key = name.lower()
    for cat in categories:
        if cat.get("title", "").lower() == key:
            return cat.get("uid")
    return None


def search_media(token, keyword):
    """按关键词搜索视频（本地过滤），返回视频列表"""
    status, data = mc.api_request("GET", "/media", token=token)
    if status != 200:
        print(f"获取视频列表失败 [{status}]")
        return []
    videos = data.get("results", data) if isinstance(data, dict) else data
    kw = keyword.lower()
    return [v for v in videos if kw in v.get("title", "").lower()]


def update_title(token, friendly_token, new_title):
    """调用 PUT /api/v1/media/{token} 更新标题，返回 (success, response)"""
    url = f"{mc.BASE_URL}/api/v1/media/{friendly_token}"
    body = urllib.parse.urlencode({"title": new_title}).encode()
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req, context=mc.ssl_ctx, timeout=30) as resp:
            return True, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return False, {"error": body}
    except Exception as e:
        return False, {"error": str(e)}


def get_current_category_uids(token, friendly_token):
    """获取视频当前分类 uid 列表"""
    status, data = mc.api_request("GET", f"/media/{friendly_token}", token=token)
    if status != 200:
        return []
    # categories_info 可能是 list 或 JSON 字符串
    cats_raw = data.get("categories_info", [])
    if isinstance(cats_raw, str):
        try:
            cats_raw = json.loads(cats_raw)
        except Exception:
            return []
    return [c.get("uid") for c in cats_raw if c.get("uid")]


def bulk_action(token, friendly_token, action, category_uids):
    """执行分类相关的批量操作"""
    payload = json.dumps({
        "media_ids": [friendly_token],
        "action": action,
        "category_uids": category_uids,
    }).encode()
    status, data = mc.api_request(
        "POST", "/media/user/bulk_actions",
        data=payload, content_type="application/json", token=token,
    )
    return status == 200, data


def replace_category(token, friendly_token, new_category_uid):
    """替换分类：移除当前所有分类，再添加新分类"""
    current_uids = get_current_category_uids(token, friendly_token)
    if current_uids:
        ok, _ = bulk_action(token, friendly_token, "remove_from_category", current_uids)
        if not ok:
            print("⚠️  移除旧分类失败，继续尝试添加新分类")
    return bulk_action(token, friendly_token, "add_to_category", [new_category_uid])


def main():
    parser = argparse.ArgumentParser(
        description="修改 MediaCMS 视频标题和分类",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("friendly_token", nargs="?", default=None,
                        help="视频 friendly_token（与 --search 二选一）")
    parser.add_argument("--search", metavar="KEYWORD", default=None,
                        help="按关键词搜索视频标题")
    parser.add_argument("--title", metavar="NEW_TITLE", default=None,
                        help="新标题")
    parser.add_argument("--category", metavar="CATEGORY_NAME", default=None,
                        help="新分类名称（会替换当前所有分类）")
    args = parser.parse_args()

    if not args.friendly_token and not args.search:
        parser.error("请指定 friendly_token 或使用 --search 搜索")
    if not args.title and not args.category:
        parser.error("请至少指定 --title 或 --category")

    try:
        mc.check_env()
    except RuntimeError as e:
        print(f"错误：{e}")
        sys.exit(1)

    print("正在登录...")
    token = mc.login()
    if not token:
        print("登录失败")
        sys.exit(1)
    print("登录成功\n")

    # 确定目标视频
    friendly_token = args.friendly_token
    if args.search:
        print(f"搜索视频: {args.search}")
        videos = search_media(token, args.search)
        if not videos:
            print("未找到匹配的视频")
            sys.exit(1)
        if len(videos) == 1:
            friendly_token = videos[0].get("friendly_token")
            print(f"找到视频: {videos[0].get('title')} ({friendly_token})")
        else:
            print(f"找到 {len(videos)} 个匹配视频：")
            for i, v in enumerate(videos, 1):
                print(f"  {i}. {v.get('title')}  (token: {v.get('friendly_token')})")
            try:
                idx = int(input("请输入序号: ")) - 1
                friendly_token = videos[idx].get("friendly_token")
            except (ValueError, IndexError):
                print("无效选择")
                sys.exit(1)

    # 查找分类 uid
    category_uid = None
    if args.category:
        categories = get_categories(token)
        category_uid = find_category_uid(categories, args.category)
        if not category_uid:
            print(f"错误：未找到分类 '{args.category}'")
            sys.exit(1)

    # 更新标题
    if args.title:
        print(f"更新标题 -> {args.title}")
        ok, data = update_title(token, friendly_token, args.title)
        if ok:
            print("✅ 标题更新成功")
        else:
            print(f"❌ 标题更新失败: {data}")

    # 替换分类
    if category_uid:
        print(f"替换分类 -> {args.category}")
        ok, data = replace_category(token, friendly_token, category_uid)
        if ok:
            print("✅ 分类替换成功")
        else:
            print(f"❌ 分类替换失败: {data}")

    print(f"\n✅ 操作完成 (token: {friendly_token})")


if __name__ == "__main__":
    main()

# 忽略 SSL 证书错误
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def login(user: str, password: str) -> Optional[str]:
    """登录获取 token"""
    url = f"{MEDIACMS_URL}/api/v1/login"
    data = urllib.parse.urlencode({"username": user, "password": password}).encode()
    req = urllib.request.Request(
        url, 
        data=data, 
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result.get("token")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return None


def get_categories(token: str) -> List[Dict[str, Any]]:
    """获取分类列表"""
    url = f"{MEDIACMS_URL}/api/v1/categories"
    req = urllib.request.Request(
        url, 
        headers={"Authorization": f"Token {token}"}, 
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data if isinstance(data, list) else data.get("results", [])
    except Exception as e:
        print(f"❌ 获取分类失败: {e}")
        return []


def search_media(token: str, query: str) -> List[Dict[str, Any]]:
    """搜索视频"""
    # 使用 media API 获取所有视频，然后本地过滤
    url = f"{MEDIACMS_URL}/api/v1/media"
    req = urllib.request.Request(
        url, 
        headers={"Authorization": f"Token {token}"}, 
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            videos = data.get("results", data) if isinstance(data, dict) else data
            # 本地过滤
            query_lower = query.lower()
            matched = [v for v in videos if query_lower in v.get("title", "").lower()]
            return matched
    except Exception as e:
        print(f"❌ 搜索视频失败: {e}")
        return []


def get_video_by_token(token: str, friendly_token: str) -> Optional[Dict[str, Any]]:
    """通过 friendly_token 获取视频详情"""
    url = f"{MEDIACMS_URL}/api/v1/media/{friendly_token}"
    req = urllib.request.Request(
        url, 
        headers={"Authorization": f"Token {token}"}, 
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"❌ 获取视频详情失败: {e}")
        return None


def set_category(token: str, friendly_token: str, category_uid: str) -> bool:
    """设置视频分类"""
    url = f"{MEDIACMS_URL}/api/v1/media/user/bulk_actions"
    
    payload = json.dumps({
        "media_ids": [friendly_token],
        "action": "add_to_category",
        "category_uids": [category_uid]
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ 设置分类失败 [{e.code}]: {error_body}")
        return False
    except Exception as e:
        print(f"❌ 设置分类失败: {e}")
        return False


def remove_from_category(token: str, friendly_token: str, category_uid: str) -> bool:
    """从分类中移除视频"""
    url = f"{MEDIACMS_URL}/api/v1/media/user/bulk_actions"
    
    payload = json.dumps({
        "media_ids": [friendly_token],
        "action": "remove_from_category",
        "category_uids": [category_uid]
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"❌ 移除分类失败: {e}")
        return False


def print_categories(categories: List[Dict[str, Any]]):
    """打印分类列表"""
    print("\n" + "=" * 60)
    print("📁 可用分类列表")
    print("=" * 60)
    for i, cat in enumerate(categories, 1):
        title = cat.get("title", "未命名")
        uid = cat.get("uid", cat.get("id", "N/A"))
        media_count = cat.get("media_count", 0)
        print(f"{i}. {title}")
        print(f"   UID: {uid}")
        print(f"   视频数: {media_count}")
        print()


def print_video_list(videos: List[Dict[str, Any]]):
    """打印视频列表"""
    print("\n" + "=" * 60)
    print(f"🔍 找到 {len(videos)} 个匹配的视频")
    print("=" * 60)
    for i, video in enumerate(videos, 1):
        title = video.get("title", "未命名")
        friendly_token = video.get("friendly_token", video.get("id", "N/A"))
        url = f"{MEDIACMS_URL}/view?m={friendly_token}"
        print(f"{i}. {title}")
        print(f"   Token: {friendly_token}")
        print(f"   链接: {url}")
        
        # 显示当前分类
        categories = video.get("categories", [])
        if categories:
            cat_names = [c.get("title", "未命名") for c in categories]
            print(f"   当前分类: {', '.join(cat_names)}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="修改 MediaCMS 视频分类",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有分类
  python update_category.py --list-categories

  # 搜索视频并修改分类
  python update_category.py --search "业主证言" --to-category "人物采访"

  # 通过视频ID修改分类
  python update_category.py --video-id "SF04tKS9C" --to-category "物业服务"
        """
    )
    
    parser.add_argument("--list-categories", action="store_true",
                        help="列出所有可用分类")
    parser.add_argument("--search", type=str, metavar="KEYWORD",
                        help="搜索视频标题关键词")
    parser.add_argument("--video-id", type=str, metavar="TOKEN",
                        help="视频 friendly_token")
    parser.add_argument("--to-category", type=str, metavar="NAME",
                        help="目标分类名称")
    parser.add_argument("--user", type=str, default=None,
                        help="用户名（可覆盖环境变量）")
    parser.add_argument("--pass", dest="password", type=str, default=None,
                        help="密码（可覆盖环境变量）")
    
    args = parser.parse_args()
    
    # 获取认证信息
    user = args.user or MEDIACMS_USER
    password = args.password or MEDIACMS_PASS
    
    if not user or not password:
        print("❌ 错误：请设置 MEDIACMS_USER 和 MEDIACMS_PASS 环境变量，或通过 --user/--pass 参数传入")
        sys.exit(1)
    
    # 登录
    print("🔐 正在登录...")
    token = login(user, password)
    if not token:
        sys.exit(1)
    print("✅ 登录成功\n")
    
    # 获取分类列表
    categories = get_categories(token)
    if not categories:
        print("❌ 无法获取分类列表")
        sys.exit(1)
    
    # 构建分类名称映射
    cat_map = {}
    for cat in categories:
        cat_title = cat.get("title", "")
        cat_map[cat_title.lower()] = cat
    
    # 处理 --list-categories
    if args.list_categories:
        print_categories(categories)
        sys.exit(0)
    
    # 检查必需参数
    if not args.to_category:
        print("❌ 错误：请指定 --to-category 参数")
        parser.print_help()
        sys.exit(1)
    
    # 查找目标分类
    target_cat_key = args.to_category.lower()
    target_category = None
    
    # 尝试精确匹配
    if target_cat_key in cat_map:
        target_category = cat_map[target_cat_key]
    else:
        # 尝试模糊匹配
        for cat_title, cat in cat_map.items():
            if target_cat_key in cat_title or cat_title in target_cat_key:
                target_category = cat
                break
    
    if not target_category:
        print(f"❌ 错误：未找到分类 '{args.to_category}'")
        print("\n可用分类：")
        for cat_title in cat_map.keys():
            print(f"  - {cat_title}")
        sys.exit(1)
    
    target_uid = target_category.get("uid", target_category.get("id"))
    print(f"🎯 目标分类: {target_category.get('title')} (UID: {target_uid})\n")
    
    # 查找要修改的视频
    videos_to_update = []
    
    if args.video_id:
        # 通过 ID 查找
        print(f"🔍 正在查找视频: {args.video_id}")
        video = get_video_by_token(token, args.video_id)
        if video:
            videos_to_update.append(video)
        else:
            print(f"❌ 未找到视频: {args.video_id}")
            sys.exit(1)
    
    elif args.search:
        # 通过搜索查找
        print(f"🔍 正在搜索: '{args.search}'")
        videos = search_media(token, args.search)
        if not videos:
            print(f"❌ 未找到匹配的视频")
            sys.exit(1)
        
        print_video_list(videos)
        
        if len(videos) == 1:
            videos_to_update = videos
        else:
            # 多个匹配，让用户确认
            print(f"⚠️ 找到 {len(videos)} 个匹配的视频")
            response = input("是否全部修改分类? (y/n): ")
            if response.lower() == 'y':
                videos_to_update = videos
            else:
                # 让用户选择
                try:
                    idx = int(input(f"请输入要修改的视频编号 (1-{len(videos)}): ")) - 1
                    if 0 <= idx < len(videos):
                        videos_to_update = [videos[idx]]
                    else:
                        print("❌ 无效的编号")
                        sys.exit(1)
                except ValueError:
                    print("❌ 无效的输入")
                    sys.exit(1)
    else:
        print("❌ 错误：请指定 --search 或 --video-id 参数")
        parser.print_help()
        sys.exit(1)
    
    # 执行分类修改
    print("\n" + "=" * 60)
    print("📝 正在修改视频分类...")
    print("=" * 60)
    
    success_count = 0
    for video in videos_to_update:
        title = video.get("title", "未命名")
        friendly_token = video.get("friendly_token", video.get("id"))
        
        print(f"\n处理: {title}")
        print(f"Token: {friendly_token}")
        
        # 设置新分类
        if set_category(token, friendly_token, target_uid):
            print(f"✅ 已添加到分类: {target_category.get('title')}")
            success_count += 1
        else:
            print(f"❌ 添加分类失败")
    
    # 汇总
    print("\n" + "=" * 60)
    print(f"📊 完成: {success_count}/{len(videos_to_update)} 个视频修改成功")
    print("=" * 60)


if __name__ == "__main__":
    main()
