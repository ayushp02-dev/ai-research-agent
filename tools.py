"""
Research tools for the AI Research Agent.

Tool 1: WebSearchTool — searches the web using DuckDuckGo.
Tool 2: WebScraperTool — fetches webpages and extracts readable text.
"""

import logging

import requests
from bs4 import BeautifulSoup

from utils import clean_text, is_safe_url, truncate_text, validate_content_type

logger = logging.getLogger(__name__)

# Configuration constants
SEARCH_TIMEOUT = 25  # seconds
FETCH_TIMEOUT = 10  # seconds
MAX_RESPONSE_SIZE = 1_000_000  # 1 MB limit on downloaded HTML
USER_AGENT = "ResearchAgent/1.0 (Educational Project)"
MIN_EXTRACT_LENGTH = 50  # minimum chars for extracted text to be useful


class WebSearchTool:
    """
    Tool 1: Search the web using DuckDuckGo.

    Uses the duckduckgo-search package (no API key required).
    Returns a list of results, each with title, url, and snippet.
    """

    def __init__(self, max_results=5):
        self.max_results = max_results
        self.name = "Web Search (DuckDuckGo)"

    def search(self, query):
        """
        Search DuckDuckGo for the given query.

        Args:
            query: The search query string.

        Returns:
            List of dicts with keys: title, url, snippet.

        Raises:
            RuntimeError: If duckduckgo-search is not installed.
            Exception: If the search request fails.
        """
        logger.info("[Tool 1] Searching DuckDuckGo for: '%s'", query)
        results = []

        try:
            from ddgs import DDGS
        except ImportError:
            logger.error("[Tool 1] ddgs package not installed")
            raise RuntimeError(
                "ddgs package is not installed. "
                "Run: pip install ddgs"
            )

        try:
            with DDGS(timeout=SEARCH_TIMEOUT) as ddgs:
                try:
                    raw_results = list(ddgs.text(query, backend="duckduckgo", max_results=self.max_results))
                except Exception:
                    raw_results = list(ddgs.text(query, max_results=self.max_results))

            for item in raw_results:
                result = {
                    "title": item.get("title", "Untitled"),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", ""),
                }
                results.append(result)

            logger.info("[Tool 1] Found %d search results", len(results))

        except Exception as e:
            logger.error("[Tool 1] Search failed: %s", e)
            raise

        return results


class WebScraperTool:
    """
    Tool 2: Fetch a webpage and extract readable text.

    Uses requests for HTTP fetching and BeautifulSoup for HTML parsing.
    Includes safety checks, timeouts, and response size limits.
    """

    def __init__(self, timeout=FETCH_TIMEOUT, max_size=MAX_RESPONSE_SIZE):
        self.timeout = timeout
        self.max_size = max_size
        self.name = "Web Scraper (BeautifulSoup)"

    def fetch_and_extract(self, url):
        """
        Fetch a URL and extract readable text content.

        Args:
            url: The webpage URL to fetch.

        Returns:
            Dict with keys: url, title, text, success, error.
            - success is True if text was extracted successfully.
            - error contains a description if something went wrong.
        """
        logger.info("[Tool 2] Fetching webpage: %s", url)

        # Safety check
        if not is_safe_url(url):
            logger.warning("[Tool 2] Blocked unsafe URL: %s", url)
            return {
                "url": url,
                "title": "",
                "text": "",
                "success": False,
                "error": "URL failed safety validation",
            }

        try:
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
            )
            response.raise_for_status()

            # Validate content type
            content_type = response.headers.get("Content-Type", "")
            if not validate_content_type(content_type):
                logger.warning("[Tool 2] Non-HTML content type: %s", content_type)
                return {
                    "url": url,
                    "title": "",
                    "text": "",
                    "success": False,
                    "error": f"Non-HTML content type: {content_type}",
                }

            # Limit response size to prevent memory issues
            content = response.text[: self.max_size]

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")

            # Remove non-content elements (scripts, styles, navigation, etc.)
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # Extract page title
            title = ""
            if soup.title and soup.title.string:
                title = clean_text(soup.title.string)

            # Extract and clean body text
            raw_text = soup.get_text(separator=" ")
            text = clean_text(raw_text)
            text = truncate_text(text, max_length=3000)

            # Check if extracted text is meaningful
            if not text or len(text) < MIN_EXTRACT_LENGTH:
                logger.warning(
                    "[Tool 2] Extracted text too short (%d chars) from: %s",
                    len(text) if text else 0,
                    url,
                )
                return {
                    "url": url,
                    "title": title,
                    "text": text,
                    "success": False,
                    "error": "Extracted text too short or empty",
                }

            logger.info(
                "[Tool 2] Successfully extracted %d chars from: %s", len(text), url
            )
            return {
                "url": url,
                "title": title,
                "text": text,
                "success": True,
                "error": None,
            }

        except requests.Timeout:
            logger.error("[Tool 2] Timeout fetching: %s", url)
            return {
                "url": url,
                "title": "",
                "text": "",
                "success": False,
                "error": "Request timed out",
            }

        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            logger.error("[Tool 2] HTTP error for %s: %s", url, status)
            return {
                "url": url,
                "title": "",
                "text": "",
                "success": False,
                "error": f"HTTP error: {status}",
            }

        except requests.RequestException as e:
            logger.error("[Tool 2] Request failed for %s: %s", url, e)
            return {
                "url": url,
                "title": "",
                "text": "",
                "success": False,
                "error": str(e),
            }

        except Exception as e:
            logger.error("[Tool 2] Unexpected error for %s: %s", url, e)
            return {
                "url": url,
                "title": "",
                "text": "",
                "success": False,
                "error": str(e),
            }
