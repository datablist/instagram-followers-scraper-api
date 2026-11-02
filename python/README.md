# Instagram Followers Scraper API — Python examples

Get followers or following users with blocking Requests or async HTTPX. Each
file contains the complete source API workflow.

## Setup

Use Python 3.12 or newer. From this `python` folder:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export DATABLIST_API_KEY='your-personal-api-key'
```

Create a key on the [Datablist API page](https://app.datablist.com/account/api).
See [costs](../README.md#cost) and [credit pack pricing](https://www.datablist.com/pricing).

## Run an example

**Synchronous, using Requests:**

```sh
python sync_requests.py
```

**Asynchronous, using HTTPX:**

```sh
python async_httpx.py
```

Both clients use background source tasks. Requests blocks during HTTP calls
and polling pauses; HTTPX uses `await` and `asyncio.sleep`.

## Customize the example

Edit the values at the bottom of either file:

```python
profiles = ["nasa", "https://www.instagram.com/natgeo/"]
scraping_type = "followers"
limit_per_profile = 100
```

Profiles can be usernames, numeric user ID strings, or Instagram profile URLs.
Use `"following"` to retrieve the accounts those profiles follow. The limit
applies to each profile; the returned count can differ from the requested limit.

The function sends these values in `settings`, with `sourceId: instagram-source`,
to `/v1/sources/tasks`. It creates one task per run, polls every three seconds,
and fetches result pages until `nextCursor` is `null`.

## Results

Each script prints the task ID, final status, credits used, and all returned
users as JSON. Each user is a flat object: Instagram ID, username, profile URL,
full name, picture URL, private/verified flags, and the starting profile's ID,
username, and URL. Relationship fields use `followerSource…` or `followingSource…`
depending on the scrape type.

See the [complete output examples](../README.md#input-and-output) for all 13
production output fields. Read actual usage from the task's `credits.used`;
status and errors also belong to the task, rather than individual users.

## When something fails

HTTP errors raise the library's normal exception. Failed or stopped tasks raise
an exception with their task ID and error. Such tasks can have partial results;
retrieve them with the [cURL results call](../README.md#try-it-with-curl).

If you stop the script, the backend task continues. List your
[source tasks](https://platform.datablist.com/docs/sources/tasks) to check its
status before creating another task.
