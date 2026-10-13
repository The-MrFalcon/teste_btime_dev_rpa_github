import argparse
import logging

from application.normalizer import normalize_scraped_story
from infrastructure.export.csv_exporter import export_stories
from infrastructure.scraping.hacker_news_scraper import HackerNewsScraper
from utils.logging_config import configurar_logging


def parse_args():
    parser = argparse.ArgumentParser(description="Coleta histórias do Hacker News via scraping.")
    parser.add_argument("--limit", type=int, default=30, help="Quantidade máxima de histórias.")
    parser.add_argument(
        "--output",
        default="data/hacker_news_scraping.csv",
        help="Caminho do CSV de saída.",
    )
    parser.add_argument("--headless", action="store_true", help="Executa o navegador sem interface.")
    return parser.parse_args()


def main():
    configurar_logging()
    args = parse_args()

    try:
        logging.info("🚀 Iniciando coleta do Hacker News via scraping.")
        scraper = HackerNewsScraper(headless=args.headless)
        raw_stories = scraper.fetch_stories(limit=args.limit)
        stories = [normalize_scraped_story(item) for item in raw_stories]
        output = export_stories(stories, args.output)
        logging.info(f"💾 {len(stories)} registros salvos em {output}.")
    except (ValueError, RuntimeError, OSError) as exc:
        logging.error(f"❌ A coleta por scraping falhou: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
