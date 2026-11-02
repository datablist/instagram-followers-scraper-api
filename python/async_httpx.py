"""Scrape Instagram followers or following with async HTTPX.

This standalone example submits profiles to the Datablist Sources API, waits
for the background task, and reads every result page. HTTP calls use await;
the three-second polling pauses use asyncio.sleep.

The source ID is instagram-source. Results are flat user objects with profile
details and fields identifying the starting profile. Status, credits, and errors
belong to the task. The script prints task usage and complete results as JSON.

Set DATABLIST_API_KEY, then run: python async_httpx.py
Edit profiles, scraping_type, and limit_per_profile in main. Profiles can be
usernames, numeric user ID strings, or Instagram profile URLs. Change
scraping_type to "following" to retrieve accounts those profiles follow.

Each run creates one task. Calls use account credits, including profile lookup.
The number of returned users can differ from the requested limit.
"""

import asyncio
import json
import os
import uuid

import httpx


async def scrape_instagram_users(
    profiles: list[str],
    api_key: str,
    scraping_type: str = "followers",
    limit_per_profile: int = 100,
) -> list[dict]:
    """Submit profiles, wait for the source task, and return all generated users."""
    tasks_url = "https://api.datablist.com/v1/sources/tasks"
    headers = {"X-API-Key": api_key}

    async with httpx.AsyncClient() as client:
        # 1. Submit the profiles and choose followers or following.
        payload = {
            "sourceId": "instagram-source",
            "uniqueId": str(uuid.uuid4()),
            "settings": {
                "profiles": profiles,
                "scrapingType": scraping_type,
                "limitPerProfile": limit_per_profile,
            },
        }
        response = await client.post(tasks_url, headers=headers, json=payload)
        response.raise_for_status()
        task = response.json()
        task_id = task["@id"]
        task_url = f"{tasks_url}/{task_id}"
        print(f"Task ID: {task_id}")

        # 2. Wait for the background task to finish.
        while task["status"] not in ("completed", "failed", "stopped"):
            await asyncio.sleep(3)
            response = await client.get(task_url, headers=headers)
            response.raise_for_status()
            task = response.json()

        print(f"Task status: {task['status']}; credits used: {task['credits']['used']}")
        if task["status"] != "completed":
            raise RuntimeError(f"Task {task_id} {task['status']}: {task.get('error')}")

        # 3. Read every result page, until nextCursor is null.
        results = []
        params = {"limit": 100}
        while True:
            response = await client.get(
                f"{task_url}/results", headers=headers, params=params
            )
            response.raise_for_status()
            page = response.json()
            results.extend(page["results"])
            next_cursor = page["nextCursor"]
            if next_cursor is None:
                break
            params["cursor"] = next_cursor

    return results


async def main() -> None:
    api_key = os.environ["DATABLIST_API_KEY"]
    profiles = ["nasa"]
    scraping_type = "followers"
    limit_per_profile = 100

    results = await scrape_instagram_users(
        profiles, api_key, scraping_type, limit_per_profile
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
