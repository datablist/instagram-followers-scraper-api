# Instagram Followers Scraper API — TypeScript example

Get followers or following users with async/await and built-in `fetch`.
All HTTP calls are in [one standalone file](example.ts).

## Setup and run

From the repository root:

```sh
export DATABLIST_API_KEY='your-personal-api-key'
npx tsx typescript/example.ts
```

With Node.js 24.3 or newer, no runner package is needed:

```sh
node typescript/example.ts
```

From this `typescript` folder, use `npx tsx example.ts` or `node example.ts`.
The script uses built-in `fetch`, `crypto.randomUUID()`, and `setTimeout`, with
no imports or project dependencies.

Create a key on the [Datablist API page](https://app.datablist.com/account/api).
See [costs](../README.md#cost) and [credit pack pricing](https://www.datablist.com/pricing).

## Customize the example

Edit the values at the bottom:

```typescript
const profiles = ["nasa", "https://www.instagram.com/natgeo/"];
const scrapingType = "followers";
const limitPerProfile = 100;
```

Profiles can be usernames, numeric user ID strings, or Instagram profile URLs.
Use `"following"` to retrieve the accounts those profiles follow. The limit
applies to each profile; the returned count can differ from the requested limit.

## How it works

The script submits `sourceId: instagram-source` with profiles in `settings`
to `/v1/sources/tasks`, polls every three seconds, then reads result pages until
`nextCursor` is `null`. Each run creates one background task.

It prints the task ID, final status, credits used, and complete user objects as
JSON. Source results are flat: Instagram ID, username, profile URL, full name,
picture URL, private/verified flags, and relationship fields identifying the
starting profile. See the [complete output examples](../README.md#input-and-output)
for all 13 production output fields, including both followers and following.

Read actual usage from the task's `credits.used`; status and errors also belong
to the task, rather than individual users.

## When something fails

HTTP errors and network failures stop the script. Failed or stopped tasks throw
an error with their task ID and error. Such tasks can have partial results;
retrieve them with the [cURL results call](../README.md#try-it-with-curl).

If you stop the script, the backend task continues. List your
[source tasks](https://platform.datablist.com/docs/sources/tasks) to check its
status before creating another task.
