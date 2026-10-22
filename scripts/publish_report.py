#!/usr/bin/env python3
"""Validate and add a single SABRDF report to the GitHub Pages JSON feed."""
import json, os, pathlib, datetime
path = pathlib.Path("data/reports.json")
payload = json.loads(path.read_text(encoding="utf-8"))
kind = os.environ["REPORT_TYPE"].strip()
title = os.environ["REPORT_TITLE"].strip()
date = os.environ["REPORT_DATE"].strip()
summary = os.environ["REPORT_SUMMARY"].strip()
source = os.environ.get("REPORT_SOURCE_URL", "").strip()
if kind not in {"daily", "weekly", "monthly"}:
    raise ValueError("Invalid report type")
datetime.date.fromisoformat(date)
if not title or not summary:
    raise ValueError("Title and summary required")
if len(title) > 180 or len(summary) > 3000:
    raise ValueError("Report exceeds length limits")
if source and not source.startswith("https://"):
    raise ValueError("Only HTTPS source URLs allowed")
report = {"id": kind + "-" + date, "type":kind, "date":date, "title":title, "summary":summary}
if source:
    report["source_url"] = source
items = [x for x in payload.get("items", []) if x.get("id") != report["id"]]
items.append(report)
items.sort(key=lambda x:(x["date"],x["id"]),reverse=True)
payload["items"] = items
payload["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"Saved {report['id']}; total {len(items)} reports")
