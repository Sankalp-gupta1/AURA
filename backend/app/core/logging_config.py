import logging
import sys


class OAuthQueryFilter(logging.Filter):
    """Do not persist Google authorization codes or state in access logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, tuple) and len(record.args) == 5:
            args = list(record.args)
            if isinstance(args[2], str) and args[2].split("?", 1)[0].startswith("/api/auth/"):
                args[2] = args[2].split("?", 1)[0]
                record.args = tuple(args)
        return True


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
    logging.getLogger("uvicorn.access").addFilter(OAuthQueryFilter())
    # Quiet down noisy third-party loggers
    for noisy in ("httpx", "googleapiclient.discovery_cache", "google_auth_httplib2"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
