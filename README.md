# clipYoinker

Hooks up to Firebase RT database, downloads clips on event, and uploads them to YT/IG.

Source of Firebase events is [AiClipy UI](https://aiclippy.vercel.app/).

## Note

- Youtube API has limit of aprox. 6 clips a day. [Here](https://developers.google.com/youtube/v3/determine_quota_cost).
- IG is flaky. There are issues with page transitions and file insert.
- TikTok requires APP aproval (missing TOS/Privacy pages in order to pass).
