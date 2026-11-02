/**
 * Scrape Instagram followers or following with async/await and built-in fetch.
 *
 * Submit profiles to the Datablist Sources API, wait for the background task,
 * and read every result page. Polling pauses for three seconds between checks.
 *
 * Set DATABLIST_API_KEY, then run from the repository root:
 * npx tsx typescript/example.ts
 * Or with Node.js 24.3 or newer: node typescript/example.ts
 *
 * Edit profiles, scrapingType, and limitPerProfile at the bottom. Profiles can
 * be usernames, numeric user ID strings, or Instagram profile URLs. Change
 * scrapingType to "following" to retrieve accounts those profiles follow.
 *
 * Each run creates one source task. Calls use account credits, including profile
 * lookup. The number of returned users can differ from the requested limit.
 * Results are flat user objects; status, credits, and errors belong to the task.
 * The script prints task usage and complete results as JSON.
 */

/** Submit profiles, wait for the source task, and return all generated users. */
async function scrapeInstagramUsers(
  profiles: string[],
  apiKey: string,
  scrapingType: string = "followers",
  limitPerProfile: number = 100,
): Promise<object[]> {
  const tasksUrl = "https://api.datablist.com/v1/sources/tasks";
  const headers = {
    "X-API-Key": apiKey,
    "Content-Type": "application/json",
  };

  // 1. Submit the profiles and choose followers or following.
  const payload = {
    sourceId: "instagram-source",
    uniqueId: crypto.randomUUID(),
    settings: {
      profiles,
      scrapingType,
      limitPerProfile,
    },
  };
  let response = await fetch(tasksUrl, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  let task = await response.json();
  const taskId = task["@id"];
  const taskUrl = `${tasksUrl}/${taskId}`;
  console.log(`Task ID: ${taskId}`);

  // 2. Wait for the background task to finish.
  while (!["completed", "failed", "stopped"].includes(task.status)) {
    await new Promise<void>((resolve) => {
      setTimeout(resolve, 3000);
    });
    response = await fetch(taskUrl, { headers });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    task = await response.json();
  }

  console.log(`Task status: ${task.status}; credits used: ${task.credits.used}`);
  if (task.status !== "completed") {
    throw new Error(`Task ${taskId} ${task.status}: ${JSON.stringify(task.error)}`);
  }

  // 3. Read every result page, until nextCursor is null.
  const results: object[] = [];
  const params = new URLSearchParams({ limit: "100" });
  while (true) {
    response = await fetch(`${taskUrl}/results?${params}`, { headers });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const page = await response.json();
    results.push(...page.results);
    if (page.nextCursor === null) {
      break;
    }
    params.set("cursor", page.nextCursor);
  }

  return results;
}

const apiKey = process.env.DATABLIST_API_KEY ?? "";
const profiles = ["nasa"];
const scrapingType = "followers";
const limitPerProfile = 100;

const results = await scrapeInstagramUsers(profiles, apiKey, scrapingType, limitPerProfile);
console.log(JSON.stringify(results, null, 2));
