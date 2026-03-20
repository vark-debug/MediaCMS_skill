---
name: MediaCMS_skill
description: |
  MediaCMS 视频管理技能。支持：(1) 上传视频并设置分类，(2) 修改视频标题和分类，(3) 查询所有分类及链接。
  使用场景：用户说"上传视频"、"帮我修改视频标题"、"修改分类"、"查看所有分类"等。
  需要环境变量：VIDEO_API_BASE_URL（服务器地址）、VIDEO_API_USERNAME（用户名）、VIDEO_API_PASSWORD（密码）
---

# MediaCMS 视频管理

## 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| VIDEO_API_BASE_URL | 服务器地址（不含末尾斜杠） | https://example.com |
| VIDEO_API_USERNAME | 用户名 | admin |
| VIDEO_API_PASSWORD | 密码 | your_password |

**配置方式（OpenClaw）：**

```json
{
  "env": {
    "VIDEO_API_BASE_URL": "https://example.com",
    "VIDEO_API_USERNAME": "admin",
    "VIDEO_API_PASSWORD": "your_password"
  }
}
```

---

## 功能一：上传视频

**脚本**：`upload.py`

```bash
# 仅上传
python3 upload.py /path/to/video.mp4 "视频标题"

# 上传并指定分类
python3 upload.py /path/to/video.mp4 "视频标题" --category "分类名称"

# 上传并设置描述
python3 upload.py /path/to/video.mp4 "视频标题" --description "视频描述" --category "分类名称"
```

**流程**：登录 → 上传 → （可选）设置分类 → 返回视频链接

---

## 功能二：修改标题 / 分类

**脚本**：`update_category.py`

```bash
# 通过 friendly_token 修改标题
python3 update_category.py <token> --title "新标题"

# 通过 friendly_token 替换分类（自动移除旧分类，添加新分类）
python3 update_category.py <token> --category "新分类名"

# 同时修改标题和分类
python3 update_category.py <token> --title "新标题" --category "新分类名"

# 先搜索再修改
python3 update_category.py --search "关键词" --title "新标题" --category "新分类名"
```

---

## 功能三：查询分类列表（含链接）

**脚本**：`list_categories.py`

```bash
# 表格形式输出（默认）
python3 list_categories.py

# JSON 格式输出
python3 list_categories.py --format json
```

## API 关键端点

- `POST /api/v1/login` - 登录获取 Token
- `GET /api/v1/categories` - 获取分类列表（需认证）
- `POST /api/v1/media` - 上传视频（需认证，multipart/form-data）
- `GET /api/v1/media?category={uid}` - 获取分类下的视频
- `POST /api/v1/media/user/bulk_actions` - 批量操作（设置分类等）

## 认证方式

Token-based Auth：登录获取 Token，后续请求使用 `Authorization: Token {token}`

## 脚本文件

| 文件名 | 功能 |
|--------|------|
| `upload.py` | 上传视频到 MediaCMS |
| `query_videos.py` | 按业务类型查询视频分类 |

## 常见问题

### 环境变量未生效

重启 OpenClaw 服务：
```bash
sh /workspace/projects/scripts/restart.sh
```

### 上传失败 - 认证错误
检查 `VIDEO_API_USERNAME` 和 `VIDEO_API_PASSWORD` 是否正确。

### SSL 证书错误
脚本已配置忽略 SSL 证书验证（针对自签名证书）。
