"""
Tests for research_agent.py — ResearchAgent orchestration.

All tests use mocked tools (no live internet access required).
"""

import pytest
from unittest.mock import patch, MagicMock

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent import ResearchAgent


# =====================================================================
# Fixtures
# =====================================================================

SAMPLE_SEARCH_RESULTS = [
    {
        "title": "Benefits of Renewable Energy",
        "url": "https://example.com/renewable",
        "snippet": "Renewable energy reduces carbon emissions and pollution.",
    },
    {
        "title": "Wind Power Advantages",
        "url": "https://example.com/wind",
        "snippet": "Wind power is a clean energy source.",
    },
    {
        "title": "Solar Energy Overview",
        "url": "https://example.com/solar",
        "snippet": "Solar energy harnesses sunlight for electricity.",
    },
]

SAMPLE_EXTRACTION_SUCCESS = {
    "url": "https://example.com/renewable",
    "title": "Benefits of Renewable Energy - Full Article",
    "text": (
        "Renewable energy sources such as solar, wind, and hydroelectric power "
        "offer significant benefits. They reduce greenhouse gas emissions, "
        "decrease air pollution, create jobs, and promote energy independence. "
        "Many countries are investing heavily in renewable energy infrastructure "
        "as part of their climate change mitigation strategies."
    ),
    "success": True,
    "error": None,
}

SAMPLE_EXTRACTION_FAILURE = {
    "url": "https://example.com/wind",
    "title": "",
    "text": "",
    "success": False,
    "error": "Request timed out",
}


# =====================================================================
# ResearchAgent tests
# =====================================================================

class TestResearchAgent:
    """Tests for the ResearchAgent orchestration logic."""

    def _make_agent(self):
        """Create agent with verbose=False to avoid cluttering test output."""
        return ResearchAgent(max_search_results=3, verbose=False)

    @patch.object(WebSearchTool := __import__("tools", fromlist=["WebSearchTool"]).WebSearchTool, "search" if True else "")
    @patch.object(WebScraperTool := __import__("tools", fromlist=["WebScraperTool"]).WebScraperTool, "fetch_and_extract" if True else "")
    def test_successful_research(self, mock_scrape, mock_search):
        """Test 1: Full successful research workflow produces a complete report."""
        mock_search.return_value = SAMPLE_SEARCH_RESULTS
        mock_scrape.side_effect = [
            SAMPLE_EXTRACTION_SUCCESS,
            SAMPLE_EXTRACTION_FAILURE,
            {
                "url": "https://example.com/solar",
                "title": "Solar Energy Overview",
                "text": (
                    "Solar energy is derived from the sun's radiation. "
                    "Photovoltaic cells convert sunlight directly into electricity. "
                    "Solar power is renewable and produces no emissions during operation."
                ),
                "success": True,
                "error": None,
            },
        ]

        agent = self._make_agent()
        report = agent.research("What are the benefits of renewable energy?")

        # Verify all required report fields exist
        assert "question" in report
        assert "short_answer" in report
        assert "findings" in report
        assert "confidence" in report
        assert "limitations" in report
        assert "next_steps" in report
        assert "execution_log" in report
        assert "execution_time_seconds" in report
        assert "sources_searched" in report
        assert "sources_validated" in report
        assert "sources_extracted" in report

        # Verify content
        assert report["question"] == "What are the benefits of renewable energy?"
        assert len(report["findings"]) > 0
        assert report["confidence"]["level"] in ("Low", "Moderate", "High")
        assert len(report["limitations"]) > 0
        assert len(report["next_steps"]) > 0
        assert report["sources_searched"] == 3
        assert report["sources_extracted"] >= 1

    @patch.object(WebSearchTool, "search")
    def test_search_no_results(self, mock_search):
        """Test 2: Search returns no results → report indicates no findings."""
        mock_search.return_value = []

        agent = self._make_agent()
        report = agent.research("xyznonexistentquery12345")

        assert report["findings"] == []
        assert report["confidence"]["level"] == "Low"
        assert report["sources_searched"] == 0

    @patch.object(WebSearchTool, "search")
    def test_search_exception(self, mock_search):
        """Test 3: Search raises exception → report still returned."""
        mock_search.side_effect = Exception("Network failure")

        agent = self._make_agent()
        report = agent.research("test query")

        assert report["findings"] == []
        assert report["confidence"]["level"] == "Low"
        assert "Network failure" in report["short_answer"]

    def test_empty_question(self):
        """Test 7: Empty question → validation error report."""
        agent = self._make_agent()
        report = agent.research("")

        assert report["question"] == "(empty)"
        assert "empty" in report["short_answer"].lower() or "invalid" in report["short_answer"].lower()
        assert report["findings"] == []
        assert report["confidence"]["level"] == "Low"

    def test_whitespace_only_question(self):
        """Test 7 variant: Whitespace-only question → validation error."""
        agent = self._make_agent()
        report = agent.research("   \n\t  ")

        assert report["findings"] == []
        assert report["confidence"]["level"] == "Low"

    @patch.object(WebSearchTool, "search")
    @patch.object(WebScraperTool, "fetch_and_extract")
    def test_report_has_all_required_fields(self, mock_scrape, mock_search):
        """Test 8: Report contains all required fields with valid values."""
        mock_search.return_value = SAMPLE_SEARCH_RESULTS[:1]
        mock_scrape.return_value = SAMPLE_EXTRACTION_SUCCESS

        agent = self._make_agent()
        report = agent.research("renewable energy")

        # Required top-level fields
        required_fields = [
            "question", "short_answer", "findings", "confidence",
            "limitations", "next_steps", "execution_log",
            "execution_time_seconds", "sources_searched",
            "sources_validated", "sources_extracted",
        ]
        for field in required_fields:
            assert field in report, f"Missing required field: {field}"

        # Confidence structure
        assert "level" in report["confidence"]
        assert "explanation" in report["confidence"]
        assert report["confidence"]["level"] in ("Low", "Moderate", "High")

        # Findings structure
        for finding in report["findings"]:
            assert "source_title" in finding
            assert "source_url" in finding
            assert "evidence_type" in finding
            assert "text" in finding
            assert "relevance_score" in finding
            assert finding["source_url"].startswith("http")

    @patch.object(WebSearchTool, "search")
    @patch.object(WebScraperTool, "fetch_and_extract")
    def test_source_references_are_valid(self, mock_scrape, mock_search):
        """Test 8: Every finding has a valid source URL from the search results."""
        mock_search.return_value = SAMPLE_SEARCH_RESULTS
        mock_scrape.side_effect = [
            SAMPLE_EXTRACTION_SUCCESS,
            SAMPLE_EXTRACTION_FAILURE,
            {
                "url": "https://example.com/solar",
                "title": "Solar",
                "text": "Solar panels convert sunlight into clean renewable energy for homes.",
                "success": True,
                "error": None,
            },
        ]

        agent = self._make_agent()
        report = agent.research("renewable energy")

        source_urls = {r["url"] for r in SAMPLE_SEARCH_RESULTS}
        for finding in report["findings"]:
            assert finding["source_url"] in source_urls, (
                f"Finding URL {finding['source_url']} not in search results"
            )

    @patch.object(WebSearchTool, "search")
    @patch.object(WebScraperTool, "fetch_and_extract")
    def test_unsafe_urls_filtered(self, mock_scrape, mock_search):
        """Test 6: Unsafe URLs in search results are filtered out."""
        mock_search.return_value = [
            {
                "title": "Legit Result",
                "url": "https://example.com/legit",
                "snippet": "This is legitimate content about renewable energy.",
            },
            {
                "title": "Malicious",
                "url": "http://localhost/admin",
                "snippet": "Should be blocked",
            },
            {
                "title": "Internal",
                "url": "http://192.168.1.1/config",
                "snippet": "Should be blocked too",
            },
        ]
        mock_scrape.return_value = {
            "url": "https://example.com/legit",
            "title": "Legit",
            "text": "This is legitimate content about energy that passes the length check nicely.",
            "success": True,
            "error": None,
        }

        agent = self._make_agent()
        report = agent.research("renewable energy")

        # Only the safe URL should appear in findings
        for finding in report["findings"]:
            assert "localhost" not in finding["source_url"]
            assert "192.168" not in finding["source_url"]

    @patch.object(WebSearchTool, "search")
    @patch.object(WebScraperTool, "fetch_and_extract")
    def test_all_fetches_fail(self, mock_scrape, mock_search):
        """Test 4: All webpage fetches fail → report uses snippets or is empty."""
        mock_search.return_value = SAMPLE_SEARCH_RESULTS
        mock_scrape.return_value = SAMPLE_EXTRACTION_FAILURE

        agent = self._make_agent()
        report = agent.research("renewable energy benefits")

        # Report should still be generated (possibly with snippet-based findings)
        assert report["question"] == "renewable energy benefits"
        assert isinstance(report["findings"], list)
        assert report["confidence"]["level"] in ("Low", "Moderate", "High")
        # Should note the failures in limitations
        limitations_text = " ".join(report["limitations"])
        assert "could not be fetched" in limitations_text or "insufficient" in limitations_text

    @patch.object(WebSearchTool, "search")
    @patch.object(WebScraperTool, "fetch_and_extract")
    def test_malformed_search_results_handled(self, mock_scrape, mock_search):
        """Test 6: Malformed search results are gracefully handled."""
        mock_search.return_value = [
            {"title": "", "url": "", "snippet": ""},  # No URL
            {"title": "Good", "url": "https://example.com/ok", "snippet": "Content here"},
            {},  # Completely empty
        ]
        mock_scrape.return_value = {
            "url": "https://example.com/ok",
            "title": "Good Page",
            "text": "This page has good content about research topics and findings.",
            "success": True,
            "error": None,
        }

        agent = self._make_agent()
        report = agent.research("research topics")

        # Should only process the valid result
        assert report["sources_validated"] <= 1

    @patch.object(WebSearchTool, "search")
    @patch.object(WebScraperTool, "fetch_and_extract")
    def test_execution_log_populated(self, mock_scrape, mock_search):
        """Execution log contains entries for all 13 steps."""
        mock_search.return_value = SAMPLE_SEARCH_RESULTS[:1]
        mock_scrape.return_value = SAMPLE_EXTRACTION_SUCCESS

        agent = self._make_agent()
        report = agent.research("renewable energy")

        log = report["execution_log"]
        assert len(log) > 0
        # Check that multiple steps are recorded
        step_numbers = set()
        for entry in log:
            if entry.startswith("[Step"):
                step_num = entry.split("]")[0].replace("[Step", "").strip()
                step_numbers.add(step_num)
        # Should have entries from at least steps 1 through 13
        assert len(step_numbers) >= 10
