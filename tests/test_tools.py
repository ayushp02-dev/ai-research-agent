"""
Tests for tools.py — WebSearchTool and WebScraperTool.

All tests use mocks (no live internet access required).
"""

import pytest
from unittest.mock import patch, MagicMock

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import WebSearchTool, WebScraperTool


# =====================================================================
# WebSearchTool tests
# =====================================================================

class TestWebSearchTool:
    """Tests for Tool 1: DuckDuckGo web search."""

    def setup_method(self):
        self.tool = WebSearchTool(max_results=3)

    @patch("tools.DDGS" if False else "ddgs.DDGS")
    def test_successful_search(self, mock_ddgs_class):
        """Test 1: Successful search returns structured results."""
        # Arrange: mock DDGS to return sample results
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.return_value = [
            {
                "title": "Benefits of Renewable Energy",
                "href": "https://example.com/renewable",
                "body": "Renewable energy reduces carbon emissions.",
            },
            {
                "title": "Solar Power Guide",
                "href": "https://example.com/solar",
                "body": "Solar panels convert sunlight to electricity.",
            },
        ]

        # Act
        results = self.tool.search("renewable energy benefits")

        # Assert
        assert len(results) == 2
        assert results[0]["title"] == "Benefits of Renewable Energy"
        assert results[0]["url"] == "https://example.com/renewable"
        assert results[0]["snippet"] == "Renewable energy reduces carbon emissions."
        assert results[1]["title"] == "Solar Power Guide"

    @patch("ddgs.DDGS")
    def test_search_no_results(self, mock_ddgs_class):
        """Test 2: Search returns no results → empty list."""
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.return_value = []

        results = self.tool.search("xyznonexistentquery12345")

        assert results == []

    @patch("ddgs.DDGS")
    def test_search_raises_exception(self, mock_ddgs_class):
        """Test 3: Search raises an exception → propagated."""
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs_class.return_value.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            self.tool.search("test query")


# =====================================================================
# WebScraperTool tests
# =====================================================================

class TestWebScraperTool:
    """Tests for Tool 2: Webpage fetching and text extraction."""

    def setup_method(self):
        self.tool = WebScraperTool(timeout=5, max_size=100_000)

    @patch("tools.requests.get")
    def test_successful_fetch_and_extract(self, mock_get):
        """Test 1: Successful fetch returns extracted text."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_response.text = """
        <html>
        <head><title>Test Page Title</title></head>
        <body>
            <h1>Main Content</h1>
            <p>This is a paragraph with enough content to pass the minimum
            length check. It contains information about renewable energy
            and its benefits for the environment and society.</p>
        </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.tool.fetch_and_extract("https://example.com/page")

        assert result["success"] is True
        assert result["url"] == "https://example.com/page"
        assert result["title"] == "Test Page Title"
        assert "renewable energy" in result["text"].lower()
        assert result["error"] is None

    @patch("tools.requests.get")
    def test_fetch_timeout(self, mock_get):
        """Test 4: Fetch times out → graceful failure."""
        import requests as req
        mock_get.side_effect = req.Timeout("Connection timed out")

        result = self.tool.fetch_and_extract("https://example.com/slow")

        assert result["success"] is False
        assert "timed out" in result["error"].lower()

    @patch("tools.requests.get")
    def test_fetch_http_error(self, mock_get):
        """Test 4: HTTP 404 error → graceful failure."""
        import requests as req
        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = req.HTTPError(response=mock_response)
        mock_get.side_effect = http_error

        result = self.tool.fetch_and_extract("https://example.com/missing")

        assert result["success"] is False
        assert "HTTP error" in result["error"]

    @patch("tools.requests.get")
    def test_fetch_empty_content(self, mock_get):
        """Test 5: Page with empty/short content → reported as failure."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.tool.fetch_and_extract("https://example.com/empty")

        assert result["success"] is False
        assert "too short" in result["error"].lower() or "empty" in result["error"].lower()

    @patch("tools.requests.get")
    def test_fetch_non_html_content(self, mock_get):
        """Test 5: Non-HTML content type → rejected."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.tool.fetch_and_extract("https://example.com/file.pdf")

        assert result["success"] is False
        assert "Non-HTML" in result["error"]

    def test_fetch_unsafe_url_localhost(self):
        """Test 6: Localhost URL is blocked."""
        result = self.tool.fetch_and_extract("http://localhost/admin")

        assert result["success"] is False
        assert "safety" in result["error"].lower()

    def test_fetch_unsafe_url_private_ip(self):
        """Test 6: Private IP is blocked (SSRF protection)."""
        result = self.tool.fetch_and_extract("http://192.168.1.1/config")

        assert result["success"] is False
        assert "safety" in result["error"].lower()

    def test_fetch_unsafe_url_non_http(self):
        """Test 6: Non-HTTP scheme is blocked."""
        result = self.tool.fetch_and_extract("file:///etc/passwd")

        assert result["success"] is False
        assert "safety" in result["error"].lower()

    @patch("tools.requests.get")
    def test_scripts_removed_from_extraction(self, mock_get):
        """Verify that script and style tags are removed during extraction."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = """
        <html>
        <head><title>Page</title></head>
        <body>
            <script>alert('malicious');</script>
            <style>.hidden { display: none; }</style>
            <p>This is safe visible content that is long enough to pass
            the minimum length threshold for extraction validation here.</p>
        </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = self.tool.fetch_and_extract("https://example.com/scripts")

        assert result["success"] is True
        assert "alert" not in result["text"]
        assert "malicious" not in result["text"]
        assert "safe visible content" in result["text"]
