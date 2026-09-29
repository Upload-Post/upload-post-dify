# Privacy Policy - Upload-Post Dify Plugin

This plugin connects Dify to the [Upload-Post](https://www.upload-post.com) API
so that your workflows and agents can publish content to social networks and
read upload status, history and analytics.

## Data collected by the plugin

The plugin itself does not collect, store or log any personal data. It has no
database, no analytics and no telemetry. It only forwards the parameters of each
tool call to the Upload-Post API and returns the API response to Dify.

## Credentials

- **Upload-Post API key**: entered by you in Dify and stored by Dify as an
  encrypted provider credential. The plugin sends it only to
  `https://api.upload-post.com` in the `Authorization` header and never writes
  it to logs or error messages.

## Data sent to third parties

Every tool call sends data to a single third-party service, Upload-Post
(`api.upload-post.com`):

| Tool | Data sent |
|------|-----------|
| Upload Text / Upload Video / Upload Photos | Profile name, target platforms, post text, titles, descriptions, first comment, schedule settings and the public URLs of the media to publish |
| Get Upload Status | The `request_id` or `job_id` |
| Get Upload History | Pagination and the filters you set |
| Get Profile Analytics | Profile name, platforms and optional page IDs |
| List Profiles | Nothing besides the API key |

Upload-Post then publishes the content to the social networks you select
(TikTok, Instagram, YouTube, LinkedIn, Facebook, X, Threads, Pinterest, Bluesky
and others). Media URLs are downloaded by Upload-Post, not by the plugin.

How Upload-Post processes and retains this data is described in its privacy
policy: https://www.upload-post.com/data-and-privacy-policy

## Data retention and deletion

The plugin retains nothing. Uploads, history and analytics are stored in your
Upload-Post account; you can delete your account and data from the Upload-Post
dashboard or by contacting support.

## Contact

Privacy questions: info@upload-post.com
