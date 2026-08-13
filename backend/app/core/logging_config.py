import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
    # Quiet down noisy third-party loggers
    for noisy in ("httpx", "googleapiclient.discovery_cache", "google_auth_httplib2"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
