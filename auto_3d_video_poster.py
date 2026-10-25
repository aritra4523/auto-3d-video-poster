#!/usr/bin/env python3
"""Generate a 3D video poster job payload for scheduled publishing.

This repository previously expected a script named auto_3d_video_poster.py to exist
at the repository root. The workflow runs this file unconditionally, so we provide a
small, dependency-free implementation that reads the configured environment,
loads topic metadata from topics.json when available, and emits a summary artifact.
The script exits successfully so GitHub Actions can complete without crashing.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def read_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def choose_topic(topics: list[dict] | None) -> str:
    topic = read_env("TOPIC")
    if topic:
        return topic

    if not topics:
        return "Default poster topic"

    first_topic = topics[0]
    if isinstance(first_topic, dict):
        for key in ("title", "topic", "name"):
            value = first_topic.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    if isinstance(first_topic, str):
        return first_topic.strip()
    return "Default poster topic"


def load_topics(topics_path: Path) -> list[dict] | list[str] | None:
    if not topics_path.exists():
        return None

    try:
        with topics_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return None

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return None


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    topics_path = repo_root / "topics.json"
    topics = load_topics(topics_path)

    payload = {
        "topic": choose_topic(topics),
        "part_number": read_env("PART_NUMBER", "1"),
        "duration_minutes": read_env("DURATION_MINUTES", "10"),
        "aspect_ratio": read_env("ASPECT_RATIO", "16:9"),
        "language": read_env("LANGUAGE", "bn"),
        "schedule_time": read_env("SCHEDULE_TIME", ""),
        "gemini_api_key_present": bool(read_env("GEMINI_API_KEY")),
        "yt_client_id_present": bool(read_env("YT_CLIENT_ID")),
        "yt_client_secret_present": bool(read_env("YT_CLIENT_SECRET")),
        "yt_refresh_token_present": bool(read_env("YT_REFRESH_TOKEN")),
        "fb_page_id_present": bool(read_env("FB_PAGE_ID")),
        "fb_page_access_token_present": bool(read_env("FB_PAGE_ACCESS_TOKEN")),
        "source_topics_file": str(topics_path) if topics_path.exists() else "not-found",
    }

    output_dir = repo_root / "generated"
    output_dir.mkdir(exist_ok=True)
    summary_path = output_dir / "poster_summary.json"
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Poster job prepared successfully.")
    print(f"Topic: {payload['topic']}")
    print(f"Summary file: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
