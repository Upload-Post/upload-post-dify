# Upload-Post

**Author:** upload-post
**Version:** 0.1.0
**Type:** tool
**Source:** https://github.com/Upload-Post/upload-post-dify
**Contact:** info@upload-post.com

## Description

[Upload-Post](https://www.upload-post.com) publishes videos, photos and text
posts to TikTok, Instagram, YouTube, LinkedIn, Facebook, X, Threads, Pinterest,
Bluesky, Discord, Telegram, Google Business and more with a single API call.

This plugin brings Upload-Post into Dify workflows, chatflows and agents: write
a post with an LLM and publish it everywhere, schedule it, check whether it went
live, and read the results and analytics.

## Tools

| Tool | What it does | API endpoint |
|------|--------------|--------------|
| **Upload Text Post** | Publish or schedule a text post (X, LinkedIn, Facebook, Threads, Bluesky, ...) | `POST /api/upload_text` |
| **Upload Video** | Publish or schedule a video from a public URL | `POST /api/upload` |
| **Upload Photos** | Publish or schedule one or more photos (carousel) from public URLs | `POST /api/upload_photos` |
| **Get Upload Status** | Status and post URLs of an upload (`request_id`) or scheduled post (`job_id`) | `GET /api/uploadposts/status` |
| **List Profiles** | Your profiles and the social accounts connected to each one | `GET /api/uploadposts/users` |
| **Get Upload History** | Paginated upload history with per-platform results and filters | `GET /api/uploadposts/history` |
| **Get Profile Analytics** | Followers, impressions, reach and engagement per platform | `GET /api/analytics/{profile}` |

Full API reference: https://docs.upload-post.com/api/reference

## Setup

1. Create an Upload-Post account at https://app.upload-post.com (there is a free plan).
2. Create a **profile** and connect the social accounts you want to post to.
3. Create an API key in the **API Keys** section: https://app.upload-post.com/api-keys
4. In Dify, install the plugin, open **Tools > Upload-Post > Authorize** and paste
   the API key. The key is checked against `GET /api/uploadposts/me`.

### Requirements

- An Upload-Post account and API key.
- Outbound HTTPS access from the Dify plugin daemon to `https://api.upload-post.com`.
- Media must be available at a **public http(s) URL** (Upload-Post downloads it).
  Local files are not supported by this plugin.

## Usage

- **Platforms** are passed as a comma-separated list, for example
  `tiktok,instagram,youtube`. The platform for X is `x`.
- **Profile** (`user`) is the Upload-Post profile name. If you don't know it, run
  **List Profiles** first; agents do this automatically.
- Video and photo uploads run asynchronously and return a `request_id`. Pass it
  to **Get Upload Status** to see when each platform finished and get the post URL.
- To schedule instead of publishing now, set **Scheduled date** (ISO-8601, for
  example `2026-12-31T18:00:00Z`) and optionally **Timezone** (`Europe/Madrid`),
  or turn on **Add to queue** to use the profile's next free queue slot. Scheduled
  posts return a `job_id`.

### Example: agent

Add the Upload-Post tools to an Agent node and prompt:

> Write a short LinkedIn and X post announcing our new feature and publish it
> from the `acme` profile.

The agent calls **List Profiles** to check the connected accounts and then
**Upload Text Post** with `platforms=linkedin,x`.

### Example: workflow

`LLM (write caption)` -> `Upload Video` (video URL from a previous node, caption
from the LLM) -> `Get Upload Status` with `{{request_id}}`.

## Privacy

See [PRIVACY.md](PRIVACY.md). The plugin stores nothing; data is sent only to
the Upload-Post API.

## Support

- Docs: https://docs.upload-post.com
- Email: info@upload-post.com
- Issues: https://github.com/Upload-Post/upload-post-dify/issues
