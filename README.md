# MediaCMS 视频管理技能

> 支持视频上传、标题/分类修改、分类查询，基于 MediaCMS REST API

## 📦 快速开始

### 1. 配置环境变量

在 OpenClaw 配置文件中添加：

```json
{
  "env": {
    "VIDEO_API_BASE_URL": "https://your-mediacms-server.com",
    "VIDEO_API_USERNAME": "your_username",
    "VIDEO_API_PASSWORD": "your_password"
  }
}
```

或通过 Shell 导出：

```bash
export VIDEO_API_BASE_URL=https://your-mediacms-server.com
export VIDEO_API_USERNAME=your_username
export VIDEO_API_PASSWORD=your_password
```

### 2. 重启 OpenClaw

```bash
sh /workspace/projects/scripts/restart.sh
```

---

## 🎯 三大功能

### 功能一：上传视频

```bash
# 仅上传
python3 upload.py /path/to/video.mp4 "视频标题"

# 上传并设置分类
python3 upload.py /path/to/video.mp4 "视频标题" --category "分类名称"

# 上传并设置描述和分类
python3 upload.py /path/to/video.mp4 "视频标题" --description "视频描述" --category "分类名称"
```

### 功能二：修改标题 / 分类

```bash
# 通过 friendly_token 修改标题
python3 update_category.py <token> --title "新标题"

# 替换分类（自动移除旧分类，添加新分类）
python3 update_category.py <token> --category "新分类名"

# 同时修改标题和分类
python3 update_category.py <token> --title "新标题" --category "新分类名"

# 搜索视频后修改
python3 update_category.py --search "关键词" --category "新分类名"
```

### 功能三：查询分类列表（返回链接）

```bash
# 表格形式输出（含视频数和链接）
python3 list_categories.py

# JSON 格式
python3 list_categories.py --format json
```

---

## 📁 文件结构

| 文件 | 功能 |
|------|------|
| `mediacms_client.py` | 公共 API 客户端（登录、请求封装） |
| `upload.py` | 上传视频到 MediaCMS |
| `update_category.py` | 修改视频标题和分类 |
| `list_categories.py` | 查询所有分类及浏览链接 |

---

## ⚙️ 环境变量说明

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `VIDEO_API_BASE_URL` | ✅ | 服务器地址，不含末尾斜杠 |
| `VIDEO_API_USERNAME` | ✅ | 登录用户名 |
| `VIDEO_API_PASSWORD` | ✅ | 登录密码 |

---

## 🐛 故障排查

### 认证失败 (HTTP 401)
检查 `VIDEO_API_USERNAME` 和 `VIDEO_API_PASSWORD` 是否正确。

### 连接失败
检查 `VIDEO_API_BASE_URL` 是否正确，服务器是否在线。

### SSL 证书错误
脚本已配置忽略自签名证书验证，无需额外处理。

## 🔐 安全提示

- **不要**将密码提交到代码仓库，始终通过环境变量传入
- 定期更换密码

