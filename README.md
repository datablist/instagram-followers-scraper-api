# Instagram Followers Scraper API

Get Instagram followers or following lists from one or more profiles with the
Datablist [Instagram Followers Scraper API](https://www.datablist.com/apis).
Send usernames, profile URLs, or numeric user IDs and retrieve user details,
profile links, private/verified flags, and the profile each relationship comes from.

Build audience research tools, discover creators, or compare the accounts followed
by brands in your market. This repository includes simple Python and TypeScript
examples you can copy into your application.

This is a **source**: it generates a list of users from your settings. It uses
`/v1/sources/tasks`, rather than the enrichment task endpoint, and needs no input
rows or Datablist collection. See the
[production source schema](https://api.datablist.com/v1/sources/instagram-source).

## Get started

Create a [Personal API Key](https://app.datablist.com/account/api), then choose an example.

**Python — Requests or async HTTPX:**

```sh
cd python
python -m pip install -r requirements.txt
export DATABLIST_API_KEY='your-personal-api-key'
python sync_requests.py
# Or: python async_httpx.py
```

**TypeScript — async/await**, from the repository root:

```sh
export DATABLIST_API_KEY='your-personal-api-key'
npx tsx typescript/example.ts
```

With Node.js 24.3 or newer, you can also run `node typescript/example.ts`.
See the [Python guide](python/README.md) and [TypeScript guide](typescript/README.md)
for setup and customization.

Each example creates one background task, polls every three seconds, then reads
all result pages. Edit the profile list, scrape type, and per-profile limit at
the bottom of the script.

## Cost

The base cost is **$1 for 1,000 credits** ($0.001 per credit, in USD).
Larger top-up packages reduce the price per credit and per record.

**0.01 credits ($0.00001) per follower or following user.** For example, 100
results cost 1 credit ($0.001) and 10,000 results cost 100 credits ($0.10),
before profile lookup charges. Resolving the starting profile can also consume
credits, even when the task returns no users.

Read `credits.used` on the task for actual usage. `limitPerProfile` sets the
requested number of users per profile; the returned count can differ, and the
limit is not a price cap. See the current
[source cost and limits](https://platform.datablist.com/docs/sources/tools/instagram-source#credits-and-limits)
and [credit pack pricing](https://www.datablist.com/pricing).

## Input and output

### Find followers

Send this JSON to `POST https://api.datablist.com/v1/sources/tasks`:

```json
{
  "sourceId": "instagram-source",
  "uniqueId": "e93682ef-cc1c-4c29-925e-9fd716d5c32a",
  "settings": {
    "profiles": [
      "nasa",
      "https://www.instagram.com/natgeo/",
      "123456789"
    ],
    "scrapingType": "followers",
    "limitPerProfile": 100
  }
}
```

The list shows a username, a full profile URL, and an example numeric user ID.

Use a fresh `uniqueId` for each new task. The API returns `202 Accepted` with
an `@id`. Poll `GET /v1/sources/tasks/{taskId}` until the status is `completed`,
`failed`, or `stopped`, then retrieve `GET /v1/sources/tasks/{taskId}/results`.

The following responses use **sample data**. Each result is a flat user object.
The three `followerSource…` fields identify the profile that user follows.

```json
{
  "taskId": "00000000000040008000000000000001",
  "results": [
    {
      "instagramUserId": "10000000001",
      "instagramUsername": "example_user",
      "instagramProfileUrl": "https://www.instagram.com/example_user/",
      "instagramFullName": "Example User",
      "instagramPicture": "https://example.com/images/example-user.jpg",
      "instagramPrivate": false,
      "instagramVerified": false,
      "followerSourceProfileId": "10000000002",
      "followerSourceProfileUsername": "nasa",
      "followerSourceProfileUrl": "https://www.instagram.com/nasa/"
    }
  ],
  "nextCursor": null
}
```

### Find accounts a profile follows

Set `scrapingType` to `following`:

```json
{
  "sourceId": "instagram-source",
  "uniqueId": "792393dc-6dbb-4c26-9426-f8a667af533a",
  "settings": {
    "profiles": [
      "nasa",
      "https://www.instagram.com/natgeo/",
      "123456789"
    ],
    "scrapingType": "following",
    "limitPerProfile": 100
  }
}
```

Here the generated users are accounts the submitted profiles follow. In this
sample response, the three `followingSource…` fields identify NASA as the
starting profile:

```json
{
  "taskId": "00000000000040008000000000000002",
  "results": [
    {
      "instagramUserId": "10000000003",
      "instagramUsername": "example_observatory",
      "instagramProfileUrl": "https://www.instagram.com/example_observatory/",
      "instagramFullName": "Example Observatory",
      "instagramPicture": "https://example.com/images/example-observatory.jpg",
      "instagramPrivate": false,
      "instagramVerified": true,
      "followingSourceProfileId": "10000000002",
      "followingSourceProfileUsername": "nasa",
      "followingSourceProfileUrl": "https://www.instagram.com/nasa/"
    }
  ],
  "nextCursor": null
}
```

These two examples show **all 13 output fields** in the production schema.
The seven `instagram…` fields describe the generated user; the six relationship
fields depend on the scrape type. Fields can be absent when data is unavailable.
When you submit several profiles, the relationship fields show where each user
came from.

### Task status and credits

Source task status, credit usage, and errors are returned on the **task**, rather
than repeated on every user. Sample completed task for the followers example:

```json
{
  "@id": "00000000000040008000000000000001",
  "@type": "SourceTask",
  "kind": "source",
  "sourceId": "instagram-source",
  "uniqueId": "e93682ef-cc1c-4c29-925e-9fd716d5c32a",
  "status": "completed",
  "createdAt": "2026-11-02T10:00:00Z",
  "startedAt": "2026-11-02T10:00:01Z",
  "finishedAt": "2026-11-02T10:00:05Z",
  "progress": {
    "results": 1
  },
  "credits": {
    "used": "1.01",
    "max": null
  },
  "error": null,
  "links": {
    "self": "https://api.datablist.com/v1/sources/tasks/00000000000040008000000000000001",
    "results": "https://api.datablist.com/v1/sources/tasks/00000000000040008000000000000001/results"
  }
}
```

The examples print the task ID, final status, credits used, and complete user
objects. There is no per-user `inputId` or `outputs` wrapper.

## Try it with cURL

Create a task with a new UUID:

```sh
export DATABLIST_API_KEY='your-personal-api-key'

curl --fail-with-body https://api.datablist.com/v1/sources/tasks \
  -H "X-API-Key: $DATABLIST_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "{
    \"sourceId\": \"instagram-source\",
    \"uniqueId\": \"$(uuidgen)\",
    \"settings\": {
      \"profiles\": [
        \"nasa\",
        \"https://www.instagram.com/natgeo/\",
        \"123456789\"
      ],
      \"scrapingType\": \"followers\",
      \"limitPerProfile\": 100
    }
  }"
```

Copy the returned `@id` into `TASK_ID`. Check the status every few seconds:

```sh
TASK_ID='paste-the-returned-task-id'

curl --fail-with-body "https://api.datablist.com/v1/sources/tasks/$TASK_ID" \
  -H "X-API-Key: $DATABLIST_API_KEY"
```

Once the task is `completed`, `failed`, or `stopped`, retrieve its results:

```sh
curl --fail-with-body "https://api.datablist.com/v1/sources/tasks/$TASK_ID/results?limit=100" \
  -H "X-API-Key: $DATABLIST_API_KEY"
```

If `nextCursor` is not `null`, fetch the next page:

```sh
curl --fail-with-body --get "https://api.datablist.com/v1/sources/tasks/$TASK_ID/results" \
  -H "X-API-Key: $DATABLIST_API_KEY" \
  --data-urlencode 'limit=100' \
  --data-urlencode 'cursor=paste-the-returned-nextCursor'
```

Continue until `nextCursor` is `null`. The Python and TypeScript examples do this
automatically. `uuidgen` is available on macOS and many Linux systems.

## Settings and limits

- `profiles`: an array of usernames, numeric user ID strings, or profile URLs.
  For example, `["nasa", "https://www.instagram.com/natgeo/", "123456789"]`.
- `scrapingType`: `followers` or `following`; the default is `followers`.
- `limitPerProfile`: a positive integer. These examples request 100 users per
  profile. Without this setting, there is no requested limit.

Each run submits one task. Datablist handles the Instagram scrape; your script
reads the generated results in pages of up to 100 users. Use `nextCursor` to
find the end, even when a page contains fewer than 100 users.

## When something fails

HTTP errors and network failures stop the examples. Failed or stopped tasks
raise an error with the task ID and task error. Such tasks can still contain
partial results: use the cURL results call above to retrieve them.

Stopping a script does not cancel its backend task. You can
[list your tasks](https://platform.datablist.com/docs/sources/tasks) to check
the status before creating another task. See the
[create-task reference](https://platform.datablist.com/docs/sources/tool-calls/instagram-source/create-task)
and [results reference](https://platform.datablist.com/docs/sources/tool-calls/instagram-source/get-task-results).

## More Datablist API examples

- [Company Name to Domain](https://github.com/datablist/company-name-to-domain-api)
- [Company Name Cleaner](https://github.com/datablist/company-name-cleaner-api)
- [Company to LinkedIn](https://github.com/datablist/company-to-linkedin-api)
- [LinkedIn Profile Finder](https://github.com/datablist/linkedin-profile-finder-api)
- [LinkedIn Profile Scraper](https://github.com/datablist/linkedin-profile-scraper-api)
- [LinkedIn Company Scraper](https://github.com/datablist/linkedin-company-scraper-api)
- [Impressum Scraper](https://github.com/datablist/impressum-scraper-api)
- [Waterfall Email Finder](https://github.com/datablist/waterfall-email-finder-api)
- [Waterfall Personal Email Finder](https://github.com/datablist/waterfall-personal-email-finder-api)
- [Waterfall Phone Finder](https://github.com/datablist/waterfall-phone-finder-api)
