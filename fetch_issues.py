#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 repos.txt 中所有 GitHub 仓库过去 24 小时的 issue 动态，输出 JSON。

用法: python fetch_issues.py
输出: stdout 打印 JSON，同时保存 digest_YYYY-MM-DD.json 到当前目录。
可选: 设置环境变量 GITHUB_TOKEN 提高 API 限流额度（不设置也能用）。
"""
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPOS_FILE = os.path.join(BASE_DIR, "repos.txt")
API = "https://api.github.com"

# Windows 控制台兼容 UTF-8 输出
sys.stdout.reconfigure(encoding="utf-8")


def read_repos():
    repos = []
    with open(REPOS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                repos.append(line)
    if not repos:
        raise SystemExit("repos.txt 为空，请至少添加一个 owner/repo")
    return repos


def gh_get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-daily-digest",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_ts(ts):
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def fetch_repo(repo, since_dt):
    since_iso = urllib.parse.quote(since_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
    url = (f"{API}/repos/{repo}/issues?state=all&since={since_iso}"
           f"&per_page=100&sort=updated&direction=desc")
    items = gh_get(url)
    issues = [i for i in items if "pull_request" not in i]

    new, updated, closed = [], [], []
    for i in issues:
        entry = {
            "number": i["number"],
            "title": i["title"],
            "state": i["state"],
            "url": i["html_url"],
            "user": (i.get("user") or {}).get("login"),
            "created_at": i["created_at"],
            "updated_at": i["updated_at"],
            "closed_at": i.get("closed_at"),
            "comments": i.get("comments", 0),
            "labels": [l["name"] for l in i.get("labels", [])],
            "body_excerpt": (i.get("body") or "")[:800],
        }
        created = parse_ts(i["created_at"])
        closed_at = parse_ts(i.get("closed_at"))
        if created and created >= since_dt:
            new.append(entry)
        elif closed_at and closed_at >= since_dt:
            closed.append(entry)
        else:
            updated.append(entry)

    repo_info = gh_get(f"{API}/repos/{repo}")
    return {
        "repo": repo,
        "open_issues_count": repo_info.get("open_issues_count"),
        "new": new,
        "updated": updated,
        "closed": closed,
    }


def main():
    repos = read_repos()
    since_dt = datetime.now(timezone.utc) - timedelta(hours=24)
    result = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "since": since_dt.isoformat(),
        "repos": [],
    }
    for repo in repos:
        try:
            result["repos"].append(fetch_repo(repo, since_dt))
        except Exception as e:
            result["repos"].append({"repo": repo, "error": str(e)})

    today = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(BASE_DIR, f"digest_{today}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n[digest saved] {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
