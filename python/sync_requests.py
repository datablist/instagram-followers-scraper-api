"""Scrape Instagram followers or following with the Datablist Sources API.

This standalone Requests example submits profiles in settings, waits for the
background task, and reads every result page. HTTP calls and the three-second
polling pauses block until they finish.

The source ID is instagram-source. Results are flat user objects with profile
details and fields identifying the starting profile. Status, credits, and errors
belong to the task. The script prints task usage and complete results as JSON.

Set DATABLIST_API_KEY, then run: python sync_requests.py
Edit profiles, scraping_type, and limit_per_profile at the bottom. Profiles can
be usernames, numeric user ID strings, or Instagram profile URLs. Change
scraping_type to "following" to retrieve accounts those profiles follow.

Each run creates one task. Calls use account credits, including profile lookup.
The number of returned users can differ from the requested limit.
"""

import json
import os
import time
import uuid

import requests


def scrape_instagram_users(
    profiles: list[str],
    api_key: str,
    scraping_type: str = "followers",
    limit_per_profile: int = 100,
) -> list[dict]:
    """Submit profiles, wait for the source task, and return all generated users."""
    tasks_url = "https://api.datablist.com/v1/sources/tasks"
    headers = {"X-API-Key": api_key}

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
    response = requests.post(tasks_url, headers=headers, json=payload)
    response.raise_for_status()
    task = response.json()
    task_id = task["@id"]
    task_url = f"{tasks_url}/{task_id}"
    print(f"Task ID: {task_id}")

    # 2. Wait for the background task to finish.
    while task["status"] not in ("completed", "failed", "stopped"):
        time.sleep(3)
        response = requests.get(task_url, headers=headers)
        response.raise_for_status()
        task = response.json()

    print(f"Task status: {task['status']}; credits used: {task['credits']['used']}")
    if task["status"] != "completed":
        raise RuntimeError(f"Task {task_id} {task['status']}: {task.get('error')}")

    # 3. Read every result page, until nextCursor is null.
    results = []
    params = {"limit": 100}
    while True:
        response = requests.get(f"{task_url}/results", headers=headers, params=params)
        response.raise_for_status()
        page = response.json()
        results.extend(page["results"])
        next_cursor = page["nextCursor"]
        if next_cursor is None:
            break
        params["cursor"] = next_cursor

    return results


if __name__ == "__main__":
    api_key = os.environ["DATABLIST_API_KEY"]
    profiles = ["nasa"]
    scraping_type = "followers"
    limit_per_profile = 100

    results = scrape_instagram_users(profiles, api_key, scraping_type, limit_per_profile)
    print(json.dumps(results, indent=2, ensure_ascii=False))
