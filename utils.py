"""
Utility functions for the AI Research Agent.

Provides URL validation, security checks, text cleaning, and deduplication.
"""

import ipaddress
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def is_safe_url(url):
    """
    Validate a URL for safety.

    Blocks:
    - Non-HTTP/HTTPS schemes (file://, ftp://, javascript:, etc.)
    - localhost and loopback addresses
    - Private and reserved IP ranges (SSRF protection)
    - URLs without a valid hostname

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL is considered safe to fetch, False otherwise.
    """
    try:
        parsed = urlparse(url)

        # Must be http or https
        if parsed.scheme not in ("http", "https"):
            logger.warning("Blocked URL with scheme: %s", parsed.scheme)
            return False

        # Must have a hostname
        if not parsed.hostname:
            logger.warning("Blocked URL with no hostname: %s", url)
            return False

        hostname = parsed.hostname.lower()

        # Block localhost variants
        blocked_hosts = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
        if hostname in blocked_hosts:
            logger.warning("Blocked localhost URL: %s", url)
            return False

        # Block private/reserved IP addresses
        try:
            ip_obj = ipaddress.ip_address(hostname)
            if ip_obj.is_private or ip_obj.is_reserved or ip_obj.is_loopback:
                logger.warning("Blocked private/reserved IP URL: %s", url)
                return False
        except ValueError:
            # hostname is a domain name, not an IP — that's fine
            pass

        return True

    except Exception:
        logger.warning("URL validation failed for: %s", url)
        return False


def validate_content_type(content_type):
    """
    Check if a Content-Type header indicates HTML content.

    Args:
        content_type: The Content-Type header value.

    Returns:
        True if the content type contains 'text/html'.
    """
    if not content_type:
        return False
    return "text/html" in content_type.lower()


def clean_text(text):
    """
    Clean extracted text by normalizing whitespace.

    Args:
        text: Raw text string.

    Returns:
        Cleaned text with normalized whitespace.
    """
    if not text:
        return ""
    # Collapse all whitespace (including newlines) to single spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate_text(text, max_length=3000):
    """
    Truncate text to a maximum length, trying to break at a sentence boundary.

    Args:
        text: The text to truncate.
        max_length: Maximum number of characters.

    Returns:
        Truncated text, with '...' appended if truncated.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]
    # Try to break at the last sentence boundary
    last_period = truncated.rfind(".")
    if last_period > max_length // 2:
        return truncated[: last_period + 1]
    return truncated + "..."


def deduplicate_results(results, key="url"):
    """
    Remove duplicate results based on a key field.

    Comparison is case-insensitive and ignores trailing slashes.

    Args:
        results: List of result dicts.
        key: The dict key to use for deduplication.

    Returns:
        List of unique results, preserving order.
    """
    seen = set()
    unique = []
    for result in results:
        val = result.get(key, "").lower().rstrip("/")
        if val and val not in seen:
            seen.add(val)
            unique.append(result)
    return unique
