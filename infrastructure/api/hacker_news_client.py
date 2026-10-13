import logging
import time
from typing import Any

import requests
from requests.exceptions import RequestException

LOGGER = logging.getLogger(__name__)
API_BASE = "https://hacker-news.firebaseio.com/v0/"
HEADERS = {"User-Agent": "BtimeDevRPADemo/1.0"}


class HackerNewsApiClient:
    def __init__(self, timeout: int = 15, retries: int = 3, delay: float = 0.25):
        self.timeout = timeout
        self.retries = retries
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_top_stories(self, limit: int = 30) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError("O limite precisa ser maior que zero.")

        story_ids = self._get_json(f"{API_BASE}topstories.json")
        if not isinstance(story_ids, list):
            raise RuntimeError("A API retornou uma lista de histórias inválida.")

        stories = []
        for story_id in story_ids[:limit]:
            try:
                item = self._get_json(f"{API_BASE}item/{story_id}.json")
                if isinstance(item, dict) and item.get("type") == "story":
                    stories.append(item)
                else:
                    LOGGER.warning(f"⚠️ Item {story_id} ignorado: resposta sem dados de história.")
            except RuntimeError as exc:
                LOGGER.warning(f"⚠️ Não foi possível obter a história {story_id}: {exc}")
            time.sleep(self.delay)

        if not stories:
            raise RuntimeError("A API não retornou histórias válidas.")
        return stories

    def _get_json(self, url: str) -> Any:
        last_error = None
        for attempt in range(self.retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 429:
                    raise RuntimeError("A API limitou temporariamente as requisições (HTTP 429).")
                response.raise_for_status()
                return response.json()
            except RuntimeError:
                raise
            except (RequestException, ValueError) as exc:
                last_error = exc
                if attempt < self.retries - 1:
                    wait = 0.5 * (2 ** attempt)
                    LOGGER.warning(f"⚠️ Falha ao consultar API: {exc}. Nova tentativa em {wait:.1f}s.")
                    time.sleep(wait)

        raise RuntimeError(f"Falha na API após {self.retries} tentativas: {last_error}")
