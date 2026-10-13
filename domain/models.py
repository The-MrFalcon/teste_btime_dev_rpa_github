from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(frozen=True)
class Story:
    id: str
    title: str
    url: str = ""
    hn_url: str = ""
    score: Optional[int] = None
    author: str = ""
    comments_count: Optional[int] = None
    published_at: str = ""
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
