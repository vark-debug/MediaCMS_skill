---
name: MediaCMS_skill
description: |
  MediaCMS video management skill. Supports: (1) uploading videos with optional category assignment,
  (2) updating video title and/or category, (3) listing all categories with browse links.
  Trigger phrases: "upload video", "update video title", "change category", "list categories", etc.
  Required env vars: VIDEO_API_BASE_URL, VIDEO_API_USERNAME, VIDEO_API_PASSWORD
---

# MediaCMS Video Management

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VIDEO_API_BASE_URL` | Server base URL (no trailing slash) | `https://media.example.com` |
| `VIDEO_API_USERNAME` | Login username | `admin` |
| `VIDEO_API_PASSWORD` | Login password | `your_password` |

**Configuration (OpenClaw):**

```json
{
  "env": {
    "VIDEO_API_BASE_URL": "https://media.example.com",
    "VIDEO_API_USERNAME": "admin",
    "VIDEO_API_PASSWORD": "your_password"
  }
}
```

---

## Feature 1: Upload Video

**Script:** `upload.py`

```bash
# Upload only
python3 upload.py /path/to/video.mp4 "Product Launch"

# Upload and assign a category
python3 upload.py /path/to/video.mp4 "Product Launch" --category "Marketing"

# Upload with description and category
python3 upload.py /path/to/video.mp4 "Product Launch" --description "Q2 launch event" --category "Marketing"
```

**Flow:** Login → Upload file → (optional) Set category → Return video URL

**Example output:**
```
Logging in...
Login successful

Uploading: /path/to/video.mp4
Title: Product Launch

✅ Upload successful!
   Title     : Product Launch
   Token     : aB3xYz9K
   Video URL : https://media.example.com/view?m=aB3xYz9K

Setting category: Marketing
✅ Category set successfully

🎉 Done! Video URL: https://media.example.com/view?m=aB3xYz9K
```

---

## Feature 2: Update Title / Category

**Script:** `update_category.py`

```bash
# Update title by friendly_token
python3 update_category.py aB3xYz9K --title "New Title"

# Replace category (removes existing categories, adds new one)
python3 update_category.py aB3xYz9K --category "Events"

# Update both title and category
python3 update_category.py aB3xYz9K --title "New Title" --category "Events"

# Search by keyword, then update
python3 update_category.py --search "launch" --title "New Title" --category "Events"
```

**Flow:** Login → (optional) Search video → Update title via PUT → Replace category via bulk_actions

**Example output — title update:**
```
Logging in...
Login successful

Updating title -> New Title
✅ Title updated successfully

✅ Done (token: aB3xYz9K)
```

**Example output — search + category update:**
```
Logging in...
Login successful

Searching videos: launch
Found 3 matching videos:
  1. Product Launch 2024  (token: aB3xYz9K)
  2. Launch Event Recap   (token: mN7qRs2T)
  3. Pre-Launch Teaser    (token: wE5uVc4P)
Please enter number: 1

Replacing category -> Events
✅ Category replaced successfully

✅ Done (token: aB3xYz9K)
```

---

## Feature 3: List Categories

**Script:** `list_categories.py`

```bash
# Table format (default)
python3 list_categories.py

# JSON format
python3 list_categories.py --format json
```

**Flow:** Login → GET /api/v1/categories → Format and print name, video count, browse link

**Example output — table:**
```
========================================================================
  Category Name                  Videos  Browse Link
  ---------------------------- -------  --------------------------------
  Marketing                         24  https://media.example.com/search?category=uid-001
  Product Demos                     18  https://media.example.com/search?category=uid-002
  Events                            11  https://media.example.com/search?category=uid-003
  Training                           6  https://media.example.com/search?category=uid-004
========================================================================
  4 categories total
```

**Example output — JSON:**
```json
[
  {
    "title": "Marketing",
    "uid": "uid-001",
    "media_count": 24,
    "url": "https://media.example.com/search?category=uid-001"
  },
  {
    "title": "Product Demos",
    "uid": "uid-002",
    "media_count": 18,
    "url": "https://media.example.com/search?category=uid-002"
  }
]
```

---

## Key API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/v1/login` | Obtain auth token |
| `GET` | `/api/v1/categories` | List all categories |
| `POST` | `/api/v1/media` | Upload video (multipart/form-data) |
| `PUT` | `/api/v1/media/{token}` | Update video title/description |
| `POST` | `/api/v1/media/user/bulk_actions` | Add/remove categories |

## Authentication

Token-based: login once to get a token, then pass `Authorization: Token <token>` on all subsequent requests.

## Script Files

| File | Purpose |
|------|---------|
| `mediacms_client.py` | Shared client (login, request wrapper) |
| `upload.py` | Upload video |
| `update_category.py` | Update title and/or category |
| `list_categories.py` | List categories with links |

## Troubleshooting

### Environment variables not taking effect
Restart OpenClaw:
```bash
sh /workspace/projects/scripts/restart.sh
```

### Upload failed — authentication error (401)
Verify `VIDEO_API_USERNAME` and `VIDEO_API_PASSWORD`.

### SSL certificate error
Scripts are configured to skip SSL verification for self-signed certificates.
