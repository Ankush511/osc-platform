#!/usr/bin/env python3
"""
Repository & Issue Seeder
=========================
Discovers 300+ popular open source repositories with beginner-friendly issues
using the GitHub Search API, adds them to the database, then syncs their issues.

Usage:
    python seed_repos.py                    # Discover repos + sync issues
    python seed_repos.py --discover-only    # Just add repos, skip issue sync
    python seed_repos.py --sync-only        # Just sync issues for existing repos
    python seed_repos.py --count 500        # Target 500 repos instead of 300

Requirements:
    - GITHUB_TOKEN in .env (personal access token with public_repo scope)
      Without a token, you're limited to 10 search requests/min.
      With a token, you get 30 search requests/min and 5000 API calls/hour.

    Generate one at: https://github.com/settings/tokens
    Scopes needed: public_repo (or just read-only access to public repos)
"""
import argparse
import asyncio
import sys
import os
import time
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.base import SessionLocal
from app.models.repository import Repository
from app.services.issue_service import IssueService
from app.core.config import settings

import httpx

GITHUB_API = "https://api.github.com"

# Search queries to find repos with beginner-friendly issues across languages
SEARCH_QUERIES = [
    'label:"good first issue" language:Python',
    'label:"good first issue" language:JavaScript',
    'label:"good first issue" language:TypeScript',
    'label:"good first issue" language:Go',
    'label:"good first issue" language:Rust',
    'label:"good first issue" language:Java',
    'label:"good first issue" language:C++',
    'label:"good first issue" language:C#',
    'label:"good first issue" language:Ruby',
    'label:"good first issue" language:PHP',
    'label:"good first issue" language:Swift',
    'label:"good first issue" language:Kotlin',
    'label:"help wanted" language:Python',
    'label:"help wanted" language:JavaScript',
    'label:"help wanted" language:TypeScript',
    'label:"help wanted" language:Go',
    'label:"help wanted" language:Rust',
    'label:"help wanted" language:Java',
    'label:"beginner-friendly" language:Python',
    'label:"beginner-friendly" language:JavaScript',
    'label:"beginner-friendly" language:TypeScript',
    'label:"first-timers-only"',
]

# Also search for popular repos directly (they tend to have good-first-issues)
REPO_SEARCH_QUERIES = [
    "stars:>5000 good-first-issues:>5",
    "stars:>2000 good-first-issues:>10",
    "stars:>1000 good-first-issues:>20",
    "stars:>500 good-first-issues:>10 language:Python",
    "stars:>500 good-first-issues:>10 language:JavaScript",
    "stars:>500 good-first-issues:>10 language:TypeScript",
    "stars:>500 good-first-issues:>5 language:Go",
    "stars:>500 good-first-issues:>5 language:Rust",
    "stars:>200 good-first-issues:>5 language:Java",
    "stars:>200 good-first-issues:>5 language:Ruby",
]


def get_headers() -> dict:
    token = settings.GITHUB_TOKEN
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def search_repos_from_issues(client: httpx.AsyncClient, query: str, per_page: int = 100) -> set:
    """Search issues and extract unique repository full_names."""
    repos = set()
    page = 1
    while page <= 3:  # max 3 pages per query (300 issues)
        params = {"q": f"is:issue is:open {query}", "per_page": per_page, "page": page, "sort": "created", "order": "desc"}
        resp = await client.get(f"{GITHUB_API}/search/issues", headers=get_headers(), params=params)
        if resp.status_code == 403:
            wait = int(resp.headers.get("Retry-After", 60))
            print(f"  Rate limited. Waiting {wait}s...")
            await asyncio.sleep(wait)
            continue
        if resp.status_code != 200:
            print(f"  Search failed ({resp.status_code}): {resp.text[:200]}")
            break
        data = resp.json()
        items = data.get("items", [])
        if not items:
            break
        for item in items:
            repo_url = item.get("repository_url", "")
            if repo_url:
                full_name = repo_url.replace("https://api.github.com/repos/", "")
                repos.add(full_name)
        page += 1
        await asyncio.sleep(2)  # be nice to the API
    return repos


async def search_repos_directly(client: httpx.AsyncClient, query: str, per_page: int = 100) -> set:
    """Search repositories directly."""
    repos = set()
    page = 1
    while page <= 3:
        params = {"q": query, "per_page": per_page, "page": page, "sort": "stars", "order": "desc"}
        resp = await client.get(f"{GITHUB_API}/search/repositories", headers=get_headers(), params=params)
        if resp.status_code == 403:
            wait = int(resp.headers.get("Retry-After", 60))
            print(f"  Rate limited. Waiting {wait}s...")
            await asyncio.sleep(wait)
            continue
        if resp.status_code != 200:
            print(f"  Search failed ({resp.status_code}): {resp.text[:200]}")
            break
        data = resp.json()
        items = data.get("items", [])
        if not items:
            break
        for item in items:
            repos.add(item["full_name"])
        page += 1
        await asyncio.sleep(2)
    return repos



async def discover_repos(target_count: int = 300) -> set:
    """Discover repos using multiple search strategies."""
    all_repos = set()

    async with httpx.AsyncClient(timeout=30) as client:
        # Strategy 1: Search issues with beginner labels
        print(f"\n--- Strategy 1: Searching issues with beginner labels ---")
        for i, query in enumerate(SEARCH_QUERIES):
            print(f"  [{i+1}/{len(SEARCH_QUERIES)}] {query[:60]}...")
            found = await search_repos_from_issues(client, query)
            new = found - all_repos
            all_repos.update(found)
            print(f"    Found {len(found)} repos ({len(new)} new) — Total: {len(all_repos)}")
            if len(all_repos) >= target_count:
                break
            await asyncio.sleep(3)  # respect search rate limit (30/min)

        # Strategy 2: Search repos directly
        if len(all_repos) < target_count:
            print(f"\n--- Strategy 2: Searching repositories directly ---")
            for i, query in enumerate(REPO_SEARCH_QUERIES):
                print(f"  [{i+1}/{len(REPO_SEARCH_QUERIES)}] {query[:60]}...")
                found = await search_repos_directly(client, query)
                new = found - all_repos
                all_repos.update(found)
                print(f"    Found {len(found)} repos ({len(new)} new) — Total: {len(all_repos)}")
                if len(all_repos) >= target_count:
                    break
                await asyncio.sleep(3)

    print(f"\nDiscovered {len(all_repos)} unique repositories.")
    return all_repos


async def fetch_repo_metadata(client: httpx.AsyncClient, full_name: str) -> Optional[dict]:
    """Fetch repository metadata from GitHub API."""
    resp = await client.get(f"{GITHUB_API}/repos/{full_name}", headers=get_headers())
    if resp.status_code == 403:
        wait = int(resp.headers.get("Retry-After", 60))
        print(f"  Rate limited. Waiting {wait}s...")
        await asyncio.sleep(wait)
        resp = await client.get(f"{GITHUB_API}/repos/{full_name}", headers=get_headers())
    if resp.status_code != 200:
        return None
    return resp.json()


async def add_repos_to_db(repo_names: set):
    """Fetch metadata and insert repos into the database."""
    db = SessionLocal()
    added = 0
    skipped = 0
    failed = 0

    existing = {r.full_name for r in db.query(Repository.full_name).all()}
    new_repos = repo_names - existing
    print(f"\n{len(existing)} repos already in DB, {len(new_repos)} new to add.")

    if not new_repos:
        print("Nothing new to add.")
        db.close()
        return

    async with httpx.AsyncClient(timeout=30) as client:
        batch = list(new_repos)
        for i, full_name in enumerate(batch):
            if (i + 1) % 25 == 0 or i == 0:
                print(f"  Fetching metadata... [{i+1}/{len(batch)}]")

            try:
                data = await fetch_repo_metadata(client, full_name)
                if not data:
                    failed += 1
                    continue

                repo = Repository(
                    github_repo_id=data["id"],
                    full_name=data["full_name"],
                    name=data["name"],
                    description=(data.get("description") or "")[:500],
                    primary_language=data.get("language"),
                    topics=data.get("topics", []),
                    stars=data.get("stargazers_count", 0),
                    forks=data.get("forks_count", 0),
                    is_active=True,
                )
                db.add(repo)
                added += 1

                # Commit in batches of 50
                if added % 50 == 0:
                    db.commit()
                    print(f"    Committed {added} repos so far...")

                await asyncio.sleep(0.5)  # ~2 requests/sec to stay well under limits

            except Exception as e:
                print(f"  Error adding {full_name}: {e}")
                db.rollback()
                failed += 1
                continue

    db.commit()
    db.close()
    print(f"\nDone: {added} added, {skipped} skipped, {failed} failed.")


async def sync_all_issues():
    """Sync issues for all active repositories using the existing IssueService."""
    db = SessionLocal()
    service = IssueService(db=db)

    repo_count = db.query(Repository).filter(Repository.is_active == True).count()
    print(f"\nSyncing issues for {repo_count} active repositories...")
    print("This may take a while depending on the number of repos and rate limits.\n")

    try:
        result = await service.sync_issues()
        print(f"\nSync complete:")
        print(f"  Repositories synced: {result.repositories_synced}")
        print(f"  Issues added:        {result.issues_added}")
        print(f"  Issues updated:      {result.issues_updated}")
        print(f"  Issues closed:       {result.issues_closed}")
        print(f"  Duration:            {result.sync_duration_seconds:.1f}s")
        if result.errors:
            print(f"  Errors ({len(result.errors)}):")
            for err in result.errors[:10]:
                print(f"    - {err}")
            if len(result.errors) > 10:
                print(f"    ... and {len(result.errors) - 10} more")
    except Exception as e:
        print(f"Sync failed: {e}")
    finally:
        db.close()


async def main():
    parser = argparse.ArgumentParser(description="Seed repositories and sync issues from GitHub")
    parser.add_argument("--discover-only", action="store_true", help="Only discover and add repos, skip issue sync")
    parser.add_argument("--sync-only", action="store_true", help="Only sync issues for existing repos")
    parser.add_argument("--count", type=int, default=300, help="Target number of repos to discover (default: 300)")
    args = parser.parse_args()

    token = settings.GITHUB_TOKEN
    if not token:
        print("WARNING: No GITHUB_TOKEN set in .env")
        print("Without a token, you're limited to 10 search requests/min and 60 API calls/hour.")
        print("Set GITHUB_TOKEN in backend/.env for much higher limits (30 search/min, 5000 calls/hr).")
        print("Generate one at: https://github.com/settings/tokens\n")
        resp = input("Continue without token? (y/n): ")
        if resp.lower() != "y":
            sys.exit(0)

    if not args.sync_only:
        repos = await discover_repos(target_count=args.count)
        await add_repos_to_db(repos)

    if not args.discover_only:
        await sync_all_issues()

    print("\nAll done.")


if __name__ == "__main__":
    asyncio.run(main())
