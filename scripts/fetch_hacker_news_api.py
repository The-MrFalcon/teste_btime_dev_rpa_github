import argparse
import logging

from application.normalizer import normalize_api_story
from infrastructure.api.hacker_news_client import HackerNewsApiClient
from infrastructure.export.csv_exporter import export_stories
from utils.logging_config import configurar_logging


def parse_args():
    parser = argparse.ArgumentParser(description="Coleta histórias do Hacker News pela API oficial.")
    parser.add_argument("--limit", type=int, default=30, help="Quantidade máxima de histórias.")
    parser.add_argument(
        "--output",
        default="data/hacker_news_api.csv",
        help="Caminho do CSV de saída.",
    )
    return parser.parse_args()


def main():
    configurar_logging()
    args = parse_args()

    try:
        logging.info("🚀 Iniciando coleta do Hacker News pela API oficial.")
        client = HackerNewsApiClient()
        raw_stories = client.fetch_top_stories(limit=args.limit)
        stories = [normalize_api_story(item) for item in raw_stories]
        output = export_stories(stories, args.output)
        logging.info(f"💾 {len(stories)} registros salvos em {output}.")
    except (ValueError, RuntimeError, OSError) as exc:
        logging.error(f"❌ A coleta via API falhou: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
