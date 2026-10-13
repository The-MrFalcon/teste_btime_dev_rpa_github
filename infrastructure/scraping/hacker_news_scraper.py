import logging
from urllib.parse import urljoin

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from utils.selenium_helpers import esperar_elemento, fechar_driver, find_elemento, iniciar_driver

LOGGER = logging.getLogger(__name__)
BASE_URL = "https://news.ycombinator.com/"


class HackerNewsScraper:
    def __init__(self, timeout=10, tentativas=3, delay=3.1, headless=False):
        self.timeout = timeout
        self.tentativas = tentativas
        self.delay = delay
        self.headless = headless

    def fetch_stories(self, limit=30):
        if limit < 1:
            raise ValueError("O limite precisa ser maior que zero.")

        driver = None
        try:
            driver = iniciar_driver(headless=self.headless)
            LOGGER.info(f"🔎 Acessando Hacker News: {BASE_URL}")
            driver.get(BASE_URL)
            rows = esperar_elemento(
                driver,
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.athing")),
                timeout=self.timeout,
                tentativas=self.tentativas,
                delay=self.delay,
            )
            stories = []

            for row in rows[:limit]:
                try:
                    story = self._extract_story(row)
                    if story:
                        stories.append(story)
                except (WebDriverException, AttributeError, ValueError) as exc:
                    LOGGER.warning(f"⚠️ História ignorada por falha na extração: {exc}")

            if not stories:
                raise RuntimeError(
                    "Nenhuma história foi encontrada. A estrutura do site pode ter mudado "
                    "ou o acesso pode estar restrito."
                )

            LOGGER.info(f"✅ {len(stories)} histórias coletadas via scraping.")
            return stories
        except TimeoutException as exc:
            raise RuntimeError("O Hacker News não apresentou histórias dentro do tempo esperado.") from exc
        except WebDriverException as exc:
            raise RuntimeError(f"Falha no navegador durante o scraping: {exc}") from exc
        finally:
            fechar_driver(driver)

    def _extract_story(self, row):
        story_id = (row.get_attribute("id") or "").strip()
        title_element = find_elemento(
            row, By.CSS_SELECTOR, "span.titleline > a", timeout=self.timeout,
            tentativas=self.tentativas, delay=self.delay
        )
        title = title_element.text.strip()
        story_url = title_element.get_attribute("href") or ""
        story_url = urljoin(BASE_URL, story_url) if story_url else ""
        subtext_rows = row.find_elements(By.XPATH, "following-sibling::tr[1]")
        subtext = subtext_rows[0] if subtext_rows else None

        score = None
        author = ""
        comments_count = None

        if subtext:
            score_elements = subtext.find_elements(By.CSS_SELECTOR, "span.score")
            author_elements = subtext.find_elements(By.CSS_SELECTOR, "a.hnuser")
            if score_elements:
                score = self._number_from_text(score_elements[0].text)
            if author_elements:
                author = author_elements[0].text.strip()
            for link in subtext.find_elements(By.CSS_SELECTOR, "a"):
                if "comment" in link.text.lower():
                    comments_count = self._number_from_text(link.text)
                    break

        if not story_id or not title:
            LOGGER.warning("⚠️ História ignorada por falta de ID ou título.")
            return None

        return {
            "id": story_id,
            "title": title,
            "url": story_url,
            "hn_url": urljoin(BASE_URL, f"item?id={story_id}"),
            "score": score,
            "author": author,
            "comments_count": comments_count,
        }

    @staticmethod
    def _number_from_text(value):
        digits = "".join(character for character in value if character.isdigit())
        return int(digits) if digits else None
