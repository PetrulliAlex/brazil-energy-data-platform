from pathlib import Path
import hashlib
import logging

import requests


SOURCE_URL = (
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/"
    "dados-abertos/arquivos/ppgn-el/"
    "producao-petroleo-m3.csv/@@download/file"
)

OUTPUT_PATH = Path(
    "data/raw/anp/oil_production/oil_production.csv"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def calculate_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def download_file(url: str) -> bytes:
    logger.info("Downloading ANP oil production dataset")

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "brazil-energy-data-platform/1.0"
        },
    )

    response.raise_for_status()

    logger.info(
        "Download completed: %.2f KB",
        len(response.content) / 1024,
    )

    return response.content


def save_raw_file(content: bytes, output_path: Path) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_bytes(content)

    logger.info("Raw file saved to %s", output_path)


def main() -> None:
    content = download_file(SOURCE_URL)

    checksum = calculate_sha256(content)

    logger.info("SHA256: %s", checksum)

    save_raw_file(
        content=content,
        output_path=OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()