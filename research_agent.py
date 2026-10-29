"""
AI Research Agent — Rule-based orchestrator.

Accepts a research question, plans the workflow, uses web search and scraping
tools, filters and ranks evidence, and generates a structured research report
with source attribution, confidence estimation, and limitation reporting.

This is explicitly a rule-based agent (no LLM). The architecture is modular
so an LLM can be integrated later for synthesis and summarization.
"""

import logging
import time

from tools import WebScraperTool, WebSearchTool
from utils import deduplicate_results, is_safe_url

logger = logging.getLogger(__name__)


# Stop words used in keyword relevance scoring
STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "can", "may", "might", "shall", "of", "in", "to", "for",
    "and", "or", "but", "not", "on", "at", "by", "from", "with", "as",
    "into", "about", "between", "through", "during", "before", "after",
    "above", "below", "up", "down", "out", "off", "over", "under",
    "that", "this", "these", "those", "it", "its", "what", "which",
    "who", "whom", "how", "why", "when", "where", "if", "then", "than",
    "so", "no", "nor", "too", "very", "just", "also", "more", "most",
})


class ResearchAgent:
    """
    Rule-based research agent that orchestrates web search and content extraction.

    Workflow:
      1. Validate input
      2. Create research plan
      3. Select tools
      4. Execute web search (Tool 1)
      5. Validate and filter search results
      6. Fetch and extract webpages (Tool 2)
      7. Rank and filter evidence
      8. Associate findings with sources
      9. Generate structured report
     10. Estimate confidence
     11. Identify limitations and next steps
     12. Record execution log
     13. Assemble final report
    """

    def __init__(self, max_search_results=5, verbose=True, step_callback=None):
        """
        Initialize the research agent.

        Args:
            max_search_results: Maximum number of search results to process.
            verbose: If True, print workflow steps to the terminal.
            step_callback: Optional callable(step_num: int, message: str) for live UI updates.
        """
        self.search_tool = WebSearchTool(max_results=max_search_results)
        self.scraper_tool = WebScraperTool()
        self.verbose = verbose
        self.step_callback = step_callback
        self.execution_log = []

    def _log_step(self, step_num, message):
        """Log a workflow step to the execution log and optionally print it."""
        entry = f"[Step {step_num:>2}] {message}"
        self.execution_log.append(entry)
        if self.step_callback:
            try:
                self.step_callback(step_num, message)
            except Exception:
                pass
        if self.verbose:
            try:
                print(f"  {entry}")
            except UnicodeEncodeError:
                safe_entry = entry.encode("ascii", errors="replace").decode("ascii")
                print(f"  {safe_entry}")
        logger.info(entry)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def research(self, question):
        """
        Execute the full 13-step research workflow.

        Args:
            question: The research question to investigate.

        Returns:
            A dict containing the structured research report with all
            required fields (question, short_answer, findings, confidence,
            limitations, next_steps, execution_log, etc.).
        """
        start_time = time.time()
        self.execution_log = []

        print(f"\n{'=' * 60}")
        print("  AI RESEARCH AGENT -- Rule-Based Orchestration")
        print(f"{'=' * 60}")
        print(f"  Question: {question}")
        print(f"{'=' * 60}\n")

        # ---- Step 1: Validate input ----
        self._log_step(1, "Validating research question...")
        if not question or not question.strip():
            return self._error_report(
                question, "Research question is empty or invalid.", start_time
            )
        question = question.strip()
        self._log_step(1, f"Question accepted: '{question}'")

        # ---- Step 2: Create research plan ----
        self._log_step(2, "Creating research plan...")
        plan = self._create_plan(question)
        for item in plan:
            self._log_step(2, f"  * {item}")

        # ---- Step 3: Select tools ----
        self._log_step(3, "Selecting research tools...")
        self._log_step(3, f"  Tool 1: {self.search_tool.name}")
        self._log_step(3, f"  Tool 2: {self.scraper_tool.name}")

        # ---- Step 4: Execute web search ----
        self._log_step(4, "Executing web search...")
        search_results = []
        search_error = None
        try:
            search_results = self.search_tool.search(question)
            self._log_step(4, f"Search returned {len(search_results)} results")
        except Exception as exc:
            search_error = str(exc)
            self._log_step(4, f"Search FAILED: {search_error}")

        # ---- Step 5: Validate and filter search results ----
        self._log_step(5, "Validating and filtering search results...")
        valid_results = self._filter_search_results(search_results)
        self._log_step(5, f"{len(valid_results)} results passed validation")

        if not valid_results:
            return self._empty_results_report(question, search_error, start_time)

        # ---- Step 6: Fetch and extract webpages ----
        self._log_step(6, "Fetching and extracting webpage content...")
        extractions = self._fetch_all_pages(valid_results)

        # ---- Step 7: Rank and filter evidence ----
        self._log_step(7, "Ranking and filtering evidence...")
        findings = self._rank_evidence(extractions, question)
        self._log_step(7, f"{len(findings)} findings after ranking")

        # ---- Step 8: Associate findings with sources ----
        self._log_step(8, "Associating findings with source URLs...")
        for finding in findings:
            self._log_step(8, f"  -> {finding['source_url']}")

        # ---- Step 9: Generate report ----
        self._log_step(9, "Generating structured research report...")

        # ---- Step 10: Estimate confidence ----
        self._log_step(10, "Estimating evidence strength...")
        confidence = self._estimate_confidence(findings, valid_results, extractions)
        self._log_step(10, f"Confidence: {confidence['level']} -- {confidence['explanation']}")

        # ---- Step 11: Identify limitations ----
        self._log_step(11, "Identifying limitations and next steps...")
        limitations = self._identify_limitations(search_error, extractions, findings)
        next_steps = self._suggest_next_steps(question, findings)

        # ---- Step 12: Record execution log ----
        self._log_step(12, "Recording execution log...")
        elapsed = round(time.time() - start_time, 2)
        self._log_step(12, f"Total execution time: {elapsed}s")

        # ---- Step 13: Assemble final report ----
        self._log_step(13, "Assembling final report...")

        report = {
            "question": question,
            "short_answer": self._generate_short_answer(question, findings),
            "findings": findings,
            "confidence": confidence,
            "limitations": limitations,
            "next_steps": next_steps,
            "execution_log": list(self.execution_log),
            "execution_time_seconds": elapsed,
            "sources_searched": len(search_results),
            "sources_validated": len(valid_results),
            "sources_extracted": sum(1 for e in extractions if e["fetch_success"]),
        }

        print(f"\n{'=' * 60}")
        print("  RESEARCH COMPLETE")
        print(f"{'=' * 60}\n")

        return report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_plan(self, question):
        """Create a simple research plan displayed to the user."""
        return [
            f"Search the web for: '{question}'",
            "Retrieve and validate top search results",
            "Fetch full webpage content from validated URLs",
            "Extract and clean readable text from pages",
            "Rank evidence by keyword relevance to the question",
            "Compile findings into a structured report with source attribution",
            "Assess confidence based on evidence quantity and quality",
        ]

    def _filter_search_results(self, search_results):
        """Filter and deduplicate search results, rejecting unsafe or empty ones."""
        valid = []
        for result in search_results:
            url = result.get("url", "")
            if not url:
                self._log_step(5, "  Skipped result with no URL")
                continue
            if not is_safe_url(url):
                self._log_step(5, f"  Blocked unsafe URL: {url}")
                continue
            if not result.get("title") and not result.get("snippet"):
                self._log_step(5, "  Skipped result with no title or snippet")
                continue
            valid.append(result)

        return deduplicate_results(valid)

    def _fetch_all_pages(self, valid_results):
        """Fetch and extract content from all validated URLs."""
        extractions = []
        total = len(valid_results)
        for i, result in enumerate(valid_results, 1):
            url = result["url"]
            self._log_step(6, f"  Fetching [{i}/{total}]: {url}")
            extracted = self.scraper_tool.fetch_and_extract(url)
            extractions.append({
                "search_title": result.get("title", ""),
                "search_snippet": result.get("snippet", ""),
                "url": url,
                "extracted_title": extracted.get("title", ""),
                "extracted_text": extracted.get("text", ""),
                "fetch_success": extracted.get("success", False),
                "fetch_error": extracted.get("error"),
            })
        return extractions

    def _rank_evidence(self, extractions, question):
        """
        Rank and filter evidence based on keyword relevance.

        Uses a simple keyword-overlap heuristic: what fraction of the
        question's non-stop-word keywords appear in the extracted text.
        """
        question_words = set(question.lower().split())
        keywords = question_words - STOP_WORDS

        findings = []
        for ext in extractions:
            # Use extracted text if available, fall back to search snippet
            text = ext.get("extracted_text", "") or ext.get("search_snippet", "")
            title = ext.get("extracted_title", "") or ext.get("search_title", "")

            if not text and not ext.get("search_snippet", ""):
                continue

            # Calculate keyword relevance score
            combined = (text + " " + title).lower()
            if keywords:
                matching = sum(1 for kw in keywords if kw in combined)
                relevance_score = matching / len(keywords)
            else:
                relevance_score = 0.5  # No meaningful keywords to match

            # Determine evidence type
            if ext["fetch_success"] and ext.get("extracted_text"):
                evidence_type = "Extracted webpage content"
            else:
                evidence_type = "Search snippet"
                text = ext.get("search_snippet", text)

            findings.append({
                "source_title": title or "Untitled",
                "source_url": ext["url"],
                "evidence_type": evidence_type,
                "text": text,
                "relevance_score": round(relevance_score, 2),
            })

        # Sort by relevance (highest first)
        findings.sort(key=lambda f: f["relevance_score"], reverse=True)

        # Strictly filter out zero-relevance results to prevent irrelevant sources from being presented
        if keywords:
            findings = [f for f in findings if f["relevance_score"] > 0.0]

        return findings

    def _estimate_confidence(self, findings, valid_results, extractions):
        """
        Estimate confidence using a transparent, documented heuristic.

        Scoring (max 5 points):
          - Extracted content count: >=3 -> +2, >=1 -> +1
          - Average keyword relevance: >=50% -> +2, >=25% -> +1
          - Unique source count: >=3 -> +1

        Mapping: 4-5 -> High, 2-3 -> Moderate, 0-1 -> Low
        Zero keyword relevance or empty findings is strictly Low.
        """
        if not findings:
            return {
                "level": "Low",
                "explanation": "No relevant findings matching the research query were retrieved.",
            }

        avg_relevance = sum(f["relevance_score"] for f in findings) / len(findings)
        if avg_relevance == 0:
            return {
                "level": "Low",
                "explanation": "Retrieved sources contain 0% keyword relevance to the question.",
            }

        # Factor 1: How many pages had extractable content
        extracted_count = sum(
            1 for f in findings if f["evidence_type"] == "Extracted webpage content"
        )
        # Factor 2: Average keyword relevance
        avg_relevance = sum(f["relevance_score"] for f in findings) / len(findings)
        # Factor 3: Source diversity
        unique_sources = len(set(f["source_url"] for f in findings))

        score = 0
        details = []

        if extracted_count >= 3:
            score += 2
            details.append(f"{extracted_count} pages had extractable content")
        elif extracted_count >= 1:
            score += 1
            details.append(f"{extracted_count} page(s) had extractable content")
        else:
            details.append("No pages had extractable content (snippets only)")

        if avg_relevance >= 0.5:
            score += 2
            details.append(f"average keyword relevance: {avg_relevance:.0%}")
        elif avg_relevance >= 0.25:
            score += 1
            details.append(f"average keyword relevance: {avg_relevance:.0%}")
        else:
            details.append(f"low keyword relevance: {avg_relevance:.0%}")

        if unique_sources >= 3:
            score += 1
            details.append(f"{unique_sources} unique sources")
        else:
            details.append(f"only {unique_sources} unique source(s)")

        # Map to confidence level
        if score >= 4:
            level = "High"
        elif score >= 2:
            level = "Moderate"
        else:
            level = "Low"

        explanation = (
            f"Confidence is {level}. Based on: {'; '.join(details)}. "
            f"(Heuristic score: {score}/5)"
        )

        return {"level": level, "explanation": explanation}

    def _identify_limitations(self, search_error, extractions, findings):
        """Identify and report the limitations of this research."""
        limitations = [
            "This is a rule-based research agent without an LLM. It uses keyword "
            "matching for relevance — it cannot deeply understand or synthesize "
            "information the way a language model would.",
        ]

        if search_error:
            limitations.append(f"Web search encountered an error: {search_error}")

        failed_fetches = sum(1 for e in extractions if not e["fetch_success"])
        if failed_fetches:
            limitations.append(
                f"{failed_fetches} webpage(s) could not be fetched or had "
                "insufficient content."
            )

        if not findings:
            limitations.append("No relevant findings could be identified.")

        limitations.append(
            "Results are limited to what DuckDuckGo returns and what can be "
            "extracted from public HTML pages. Paywalled, JavaScript-rendered, "
            "or dynamic content may be inaccessible."
        )

        limitations.append(
            "Confidence estimation uses a simple heuristic based on source count, "
            "keyword relevance, and content extraction success — not statistical "
            "analysis or expert evaluation."
        )

        return limitations

    def _suggest_next_steps(self, question, findings):
        """Suggest next steps for further research."""
        steps = []
        if not findings:
            steps.append("Rephrase the question with more specific keywords.")

        steps.extend([
            "Verify key findings by visiting the original source URLs directly.",
            "Cross-reference findings with academic databases or authoritative sources.",
            "Narrow the research question for more targeted results.",
            "Consider integrating an LLM for deeper synthesis and summarization.",
        ])
        return steps

    def _generate_short_answer(self, question, findings):
        """Generate a brief answer based on the top-ranked finding."""
        if not findings:
            return (
                "The research agent could not find sufficient evidence to answer "
                "this question. Please try rephrasing with more specific terms."
            )

        top = findings[0]
        text = top["text"]

        # Take the first ~300 characters, breaking at a sentence boundary
        if len(text) > 300:
            truncated = text[:300]
            last_period = truncated.rfind(".")
            if last_period > 100:
                summary = truncated[: last_period + 1]
            else:
                summary = truncated + "..."
        else:
            summary = text

        return (
            f"Based on {len(findings)} source(s), here is what was found: "
            f"{summary} (Source: {top['source_title']})"
        )

    def _error_report(self, question, error_message, start_time):
        """Generate a report for input validation failures."""
        elapsed = round(time.time() - start_time, 2)
        return {
            "question": question or "(empty)",
            "short_answer": error_message,
            "findings": [],
            "confidence": {"level": "Low", "explanation": error_message},
            "limitations": [error_message],
            "next_steps": ["Provide a valid, non-empty research question."],
            "execution_log": list(self.execution_log),
            "execution_time_seconds": elapsed,
            "sources_searched": 0,
            "sources_validated": 0,
            "sources_extracted": 0,
        }

    def _empty_results_report(self, question, search_error, start_time):
        """Generate a report when no valid search results were found."""
        elapsed = round(time.time() - start_time, 2)

        if search_error:
            answer = (
                f"Web search failed: {search_error}. "
                "No results could be retrieved."
            )
        else:
            answer = (
                "The search returned no usable results for this question. "
                "Try rephrasing with more specific keywords."
            )

        return {
            "question": question,
            "short_answer": answer,
            "findings": [],
            "confidence": {
                "level": "Low",
                "explanation": "No valid search results were found to analyze.",
            },
            "limitations": [
                "No results were available to analyze.",
                search_error or "Search returned no matching results.",
            ],
            "next_steps": [
                "Rephrase the question with different or more specific keywords.",
                "Check your internet connection.",
                "Try again later — the search service may be temporarily unavailable.",
            ],
            "execution_log": list(self.execution_log),
            "execution_time_seconds": elapsed,
            "sources_searched": 0,
            "sources_validated": 0,
            "sources_extracted": 0,
        }
