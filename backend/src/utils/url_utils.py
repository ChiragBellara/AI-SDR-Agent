import re
from logger.universal_logger import setup_logger

logger = setup_logger(__name__)


def clean_title(title: str) -> str:
    """Clean up a title by removing dates, trailing periods or quotes, and truncating if needed."""
    if not title:
        return ""

    original_title = title

    title = title.strip().rstrip('.').strip('"\'')
    title = re.sub(r'^\d{4}[-\s]*\d{1,2}[-\s]*\d{1,2}[-\s]*', '', title)
    title = title.strip('- ').strip()

    if not title:
        logger.warning(
            f"Title became empty after cleaning: '{original_title}'")
        return ""

    if title != original_title:
        logger.info(f"Cleaned title from '{original_title}' to '{title}'")

    return title
