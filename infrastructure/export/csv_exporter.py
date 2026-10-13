import csv
from pathlib import Path
from typing import Iterable

from domain.models import Story

FIELDS = [
    "id",
    "title",
    "url",
    "hn_url",
    "score",
    "author",
    "comments_count",
    "published_at",
    "source",
]


def export_stories(stories: Iterable[Story], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for story in stories:
            writer.writerow(story.to_dict())

    return path
