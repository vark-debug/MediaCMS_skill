# MediaCMS 视频管理技能

> 基于 MediaCMS REST API，支持视频上传、标题/分类修改和分类查询。

**Language / 语言：** [English](README.md) | 中文

---

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

## 🎯 功能介绍

### 功能一：上传视频

```bash
# 仅上传
python3 upload.py /path/to/video.mp4 "我的视频标题"

# 上传并指定分类
python3 upload.py /path/to/video.mp4 "我的视频标题" --category "产品演示"

# 上传并设置描述和分类
python3 upload.py /path/to/video.mp4 "我的视频标题" --description "Q1 发布活动" --category "产品演示"
```

### 功能二：修改标题 / 分类

```bash
# 通过 friendly_token 修改标题
python3 update_category.py <token> --title "新标题"

# 替换分类（自动移除旧分类，添加新分类）
python3 update_category.py <token> --category "新分类"

# 同时修改标题和分类
python3 update_category.py <token> --title "新标题" --category "新分类"

# 按关键词搜索后修改
python3 update_category.py --search "关键词" --category "新分类"
```

### 功能三：查询分类列表（含链接）

```bash
# 表格格式输出（默认）
python3 list_categories.py

# JSON 格式输出
python3 list_categories.py --format json
```

---

## 📁 文件结构

| 文件 | 功能 |
|------|------|
| `mediacms_client.py` | 公共 API 客户端（登录、请求封装） |
| `upload.py` | 上传视频到 MediaCMS |
| `update_category.py` | 修改视频标题和/或分类 |
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

### 认证失败（HTTP 401）
检查 `VIDEO_API_USERNAME` 和 `VIDEO_API_PASSWORD` 是否正确。

### 连接失败
检查 `VIDEO_API_BASE_URL` 是否正确，以及服务器是否在线。

### SSL 证书错误
脚本已配置忽略自签名证书验证，无需额外处理。

## 🔐 安全提示

- **不要**将密码提交到代码仓库，始终通过环境变量传入。
- 定期更换密码。

---

## � 相关链接

- [MediaCMS 官方网站](https://mediacms.io)
- [MediaCMS GitHub 仓库](https://github.com/mediacms-io/mediacms)
- [MediaCMS API 文档](https://demo.mediacms.io/swagger/)
- [MediaCMS 开发者文档](https://github.com/mediacms-io/mediacms/blob/main/docs/developers_docs.md)
- [MediaCMS 演示站点](https://demo.mediacms.io)

---

## �📄 许可证

MIT 许可证 — 详见 [LICENSE](LICENSE)。
