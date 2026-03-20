# MediaCMS Video Management Skill

> Upload videos, update titles/categories, and list categories — powered by the MediaCMS REST API.

**Language / 语言：** English | [中文](README_zh.md)

## 📦 Quick Start

### 1. Set Environment Variables

Add the following to your OpenClaw config file:

```json
{
  "env": {
    "VIDEO_API_BASE_URL": "https://your-mediacms-server.com",
    "VIDEO_API_USERNAME": "your_username",
    "VIDEO_API_PASSWORD": "your_password"
  }
}
```

Or export them in your shell:

```bash
export VIDEO_API_BASE_URL=https://your-mediacms-server.com
export VIDEO_API_USERNAME=your_username
export VIDEO_API_PASSWORD=your_password
```

### 2. Restart OpenClaw

```bash
sh /workspace/projects/scripts/restart.sh
```

---

## 🎯 Features

### Feature 1: Upload Video

```bash
# Upload only
python3 upload.py /path/to/video.mp4 "My Video Title"

# Upload and assign a category
python3 upload.py /path/to/video.mp4 "My Video Title" --category "Product Demos"

# Upload with description and category
python3 upload.py /path/to/video.mp4 "My Video Title" --description "Q1 launch video" --category "Product Demos"
```

### Feature 2: Update Title / Category

```bash
# Update title by friendly_token
python3 update_category.py <token> --title "New Title"

# Replace category (removes old categories, adds new one)
python3 update_category.py <token> --category "New Category"

# Update both title and category
python3 update_category.py <token> --title "New Title" --category "New Category"

# Search by keyword, then update
python3 update_category.py --search "keyword" --category "New Category"
```

### Feature 3: List Categories (with links)

```bash
# Table format (default)
python3 list_categories.py

# JSON format
python3 list_categories.py --format json
```

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `mediacms_client.py` | Shared API client (login, request helpers) |
| `upload.py` | Upload a video to MediaCMS |
| `update_category.py` | Update video title and/or category |
| `list_categories.py` | List all categories with browse links |

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VIDEO_API_BASE_URL` | ✅ | Server base URL, no trailing slash |
| `VIDEO_API_USERNAME` | ✅ | Login username |
| `VIDEO_API_PASSWORD` | ✅ | Login password |

---

## 🐛 Troubleshooting

### Authentication failed (HTTP 401)
Verify `VIDEO_API_USERNAME` and `VIDEO_API_PASSWORD` are correct.

### Connection failed
Verify `VIDEO_API_BASE_URL` is reachable and the server is online.

### SSL certificate error
The scripts are configured to skip self-signed certificate verification — no extra action needed.

## 🔐 Security Notes

- **Never** commit passwords to a repository — always pass credentials via environment variables.
- Rotate passwords regularly.

---

## � Related Links

- [MediaCMS Official Website](https://mediacms.io)
- [MediaCMS GitHub Repository](https://github.com/mediacms-io/mediacms)
- [MediaCMS API Documentation](https://demo.mediacms.io/swagger/)
- [MediaCMS Developer Docs](https://github.com/mediacms-io/mediacms/blob/main/docs/developers_docs.md)
- [MediaCMS Demo Instance](https://demo.mediacms.io)

---

## �📄 License

MIT License — see [LICENSE](LICENSE) for details.

