import structlog
import logging
import sys
from app.config import settings

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

def get_logger():
    """Returns a logger pre-bound with the mandatory fields from OBSERVABILITY_GUIDE.md §2.1."""
    return structlog.get_logger().bind(
        poc_id=settings.poc_id,
        phase=settings.phase,
        associate_id=settings.associate_id,
    )