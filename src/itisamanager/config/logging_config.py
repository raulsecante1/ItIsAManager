import logging
import sys


def setup_logging(lvl=logging.INFO) -> None:
    logging.basicConfig(
        level=lvl,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                "agent_logs.log",
                encoding="utf-8",
            ),
        ],
    )

    # Enable httpx and OpenRouter log
    logging.getLogger("httpx").setLevel(logging.DEBUG)
    logging.getLogger("openrouter").setLevel(logging.DEBUG)