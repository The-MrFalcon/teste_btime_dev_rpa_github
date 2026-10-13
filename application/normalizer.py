from datetime import datetime, timezone
from typing import Any

from domain.models import Story


def normalize_api_story(item: dict[str, Any]) -> Story:
    timestamp = item.get("time")
    published_at = ""
    if isinstance(timestamp, (int, float)):
        published_at = datetime.fromtimestamp(
            timestamp, tz=timezone.utc
        ).isoformat()

    story_id = item.get("id", "")
    return Story(
        id=str(story_id),
        title=str(item.get("title") or "").strip(),
        url=str(item.get("url") or ""),
        hn_url=f"https://news.ycombinator.com/item?id={story_id}" if story_id else "",
        score=_optional_int(item.get("score")),
        author=str(item.get("by") or ""),
        comments_count=_optional_int(item.get("descendants")),
        published_at=published_at,
        source="api",
    )


def normalize_scraped_story(item: dict[str, Any]) -> Story:
    return Story(
        id=str(item.get("id") or ""),
        title=str(item.get("title") or "").strip(),
        url=str(item.get("url") or ""),
        hn_url=str(item.get("hn_url") or ""),
        score=_optional_int(item.get("score")),
        author=str(item.get("author") or ""),
        comments_count=_optional_int(item.get("comments_count")),
        published_at="",
        source="scraping",
    )


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None and str(value).strip() else None
    except (TypeError, ValueError):
        return None
