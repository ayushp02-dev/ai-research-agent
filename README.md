# AI Research Agent

> **Autonomous AI Research Agent Platform**  
> An autonomous, rule-based research agent architecture featuring deterministic orchestration, multi-tool delegation, strict security isolation, and transparent evidence synthesis.

---

## 1. Project Title & Overview

The **AI Research Agent** is a modular Python-based research system designed to take an open-ended research question, formulate an execution plan, autonomously orchestrate search and web scraping tools, filter and rank retrieved evidence, and assemble a structured research report with comprehensive source attribution, transparent confidence heuristics, and documented limitations.

Unlike opaque chatbot wrappers, the agent features an **explicit, visible 13-step orchestration pipeline** that prints each operational phase to the terminal, allowing evaluators and developers to observe the agent's internal decision-making process in real time.

---

## 2. Problem Statement

Modern information retrieval requires navigating millions of unstructured web pages, filtering irrelevant content, verifying source authenticity, and presenting structured conclusions. Many existing AI solutions suffer from:
1. **Opaque decision-making**: Users cannot see how evidence was gathered or whether citations are authentic.
2. **Hallucination & fabricated citations**: Generating realistic-sounding URLs that do not actually exist.
3. **Fragile dependencies**: Complete reliance on paid, rate-limited, or closed-source LLM APIs.
4. **Security oversights**: Blindly fetching arbitrary URLs, exposing systems to Server-Side Request Forgery (SSRF) and malicious scripts.

This project addresses these challenges by building an observable, reliable, self-contained research agent with strict security boundaries, robust failure handling, and zero external API costs.

---

## 3. Features

- **Visible 13-Step Orchestration**: Full transparency from query validation to final report synthesis.
- **Dual Real-World Tooling**:
  - `Tool 1: WebSearchTool` powered by DuckDuckGo (`ddgs`) with zero API keys or rate-limit subscriptions.
  - `Tool 2: WebScraperTool` powered by `requests` and `BeautifulSoup4` with script/style stripping and length validation.
- **Enterprise-Grade Security (SSRF Protection)**: Rejection of private IP spaces (RFC 1918), loopback (`localhost`, `127.0.0.1`), and non-HTTP protocols (`file://`, `ftp://`).
- **Verifiable Citation Tracking**: 100% genuine attributionâ€”every reported finding is tied to its verified source URL and title.
- **Deterministic Confidence Heuristic**: Transparent 5-point evidence scoring based on content extraction success, keyword relevance, and source diversity.
- **Resilient Failure Recovery**: Automatic fallback to search snippets when scraping is blocked (e.g., HTTP 403/404/500 or timeouts), without terminating execution.
- **Zero-Relevance Detection**: Correctly flags obscure or gibberish queries and reports Low confidence rather than presenting irrelevant text as reliable findings.
- **100% Offline Test Suite**: 23 automated `pytest` tests mocking all network requests, executing in under 2 seconds.

---

## 4. Architecture & Workflow

The architecture follows a clear pipeline design where concerns are strictly separated across modular components:

```
+-------------------------------------------------------------------------+
|                              User Query                                 |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                      [Step 1] Input Validation                          |
|             (Rejects empty, whitespace, or malformed queries)           |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                      [Step 2] Research Planner                          |
|            (Formulates deterministic 7-point execution plan)            |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                      [Step 3] Tool Selection                            |
|             (Identifies and binds WebSearchTool & WebScraperTool)       |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|               [Step 4] Tool 1: Web Search (DuckDuckGo)                  |
|           (Executes search query; catches engine timeouts)              |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|               [Step 5] Search Result Validation & Filter                |
|       (SSRF protection, scheme validation, URL deduplication)           |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|              [Step 6] Tool 2: Web Scraper (BeautifulSoup)               |
|      (Fetches HTML, validates Content-Type, strips script/style tags)   |
|         [Fallback: Uses search snippet if HTTP fetch fails]             |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|             [Step 7 & 8] Evidence Ranking & Source Linking              |
|        (Calculates keyword relevance; maps findings to exact URLs)      |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|          [Step 9 - 13] Report Synthesis & Confidence Assessment         |
|     (Heuristic scoring, limitation identification, next steps)          |
+------------------------------------+------------------------------------+
```

### Component Structure
- `app.py`: Modern Streamlit interactive web dashboard with live orchestration tracking, evidence cards, metrics, and report export.
- `main.py`: Command-line interface, CLI argument parsing, interactive prompt, report formatting, and UTF-8 console safeguards.
- `research_agent.py`: Central orchestrator implementing the 13-step research lifecycle, evidence ranking, and confidence heuristics.
- `tools.py`: Tool 1 (`WebSearchTool`) and Tool 2 (`WebScraperTool`) implementations with timeout controls and response limits.
- `utils.py`: Security validation routines (SSRF checks, private IP filtering, URL parsing, text cleaning, and deduplication).

---

## 5. Explanation of Both Tools

### Tool 1: `WebSearchTool` (DuckDuckGo via `ddgs`)
- **Purpose**: Discovers relevant web resources without requiring proprietary search API subscriptions (like Google Custom Search or Bing).
- **Implementation**: Utilizes the modern `ddgs` Python library. Configured to query DuckDuckGo directly with automatic engine fallback and a 25-second connection timeout.
- **Safety Controls**: Limits maximum returned items (default: 5) to prevent network congestion. Normalizes and validates all incoming URLs before passing downstream.

### Tool 2: `WebScraperTool` (HTTP Fetching & HTML Parsing)
- **Purpose**: Fetches the underlying HTML of verified URLs and extracts readable prose.
- **Implementation**: Uses `requests` for HTTP GET requests and `BeautifulSoup4` (`html.parser`) for DOM parsing.
- **Safety Controls**:
  - **Custom User-Agent**: Sends identifiable User-Agent header (`ResearchAgent/1.0`).
  - **Content-Type Validation**: Rejects non-HTML binary payloads (PDFs, ZIPs, images) before parsing.
  - **Size Guard**: Capped at 1,000,000 bytes (1 MB) to prevent denial-of-service via huge payloads.
  - **DOM Sanitization**: Automatically deletes `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, and `<aside>` elements to isolate genuine body content.
  - **Fallback Mechanism**: If a site blocks programmatic access (e.g., HTTP 403 Forbidden or timeout), the tool logs the incident and provides the search engine's snippet as an alternate evidence record.

---

## 6. Installation Instructions for Windows

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14 installed on your Windows machine.
- Git (optional, for repository cloning).

### Steps
1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd C:\Users\ayush\ai-research-agent
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

---

## 7. Exact Commands to Run the Project

### Launch the Modern Streamlit Web UI (Recommended)
Launch the interactive web dashboard in your default browser:
```powershell
streamlit run app.py
```

### CLI: Basic Research Query
```powershell
python main.py "What are the benefits of renewable energy?"
```

### Specifying Maximum Search Results
```powershell
python main.py --max-results 3 "How does photosynthesis work?"
```

### Output in Raw JSON Format
```powershell
python main.py --json "What is quantum computing?"
```

### Interactive Mode
Simply run the script with no arguments to enter an interactive prompt:
```powershell
python main.py
```

### Verbose / Debug Mode
```powershell
python main.py --verbose "What are the latest developments in AI?"
```

---

## 8. How to Run Tests

The automated test suite runs completely offline using mocks. No active internet connection is required.

Run the full test suite with detailed output:
```powershell
pytest tests/ -v
```

### Test Coverage Highlights (23 Tests Total)
- `test_successful_search`: Verifies structured result formatting from DuckDuckGo.
- `test_search_no_results`: Confirms clean empty list handling when no results exist.
- `test_search_raises_exception`: Tests propagation and logging of search engine errors.
- `test_successful_fetch_and_extract`: Validates HTML parsing and DOM element stripping.
- `test_fetch_timeout`: Validates timeout handling when servers are unresponsive.
- `test_fetch_http_error`: Verifies graceful response to HTTP 404/403/500 errors.
- `test_fetch_empty_content`: Rejects empty or sub-threshold web pages.
- `test_fetch_non_html_content`: Verifies rejection of non-HTML payloads (PDFs, images).
- `test_fetch_unsafe_url_localhost`: Validates blocking of `localhost` / `127.0.0.1`.
- `test_fetch_unsafe_url_private_ip`: Validates blocking of private IP ranges (SSRF prevention).
- `test_fetch_unsafe_url_non_http`: Rejects `file:///` and other non-HTTP schemes.
- `test_scripts_removed_from_extraction`: Proves malicious `<script>` tags are deleted before text processing.
- `test_empty_question` & `test_whitespace_only_question`: Verifies input validation at Step 1.
- `test_report_has_all_required_fields`: Enforces strict report dictionary schema compliance.
- `test_source_references_are_valid`: Ensures every finding points to a validated source URL.
- `test_unsafe_urls_filtered`: Confirms malicious URLs in search results are never queried.
- `test_execution_log_populated`: Asserts that execution log records all workflow phases.

---

## 9. Sample Command & Output

### Command
```powershell
python main.py "What are the benefits of renewable energy?"
```

### Actual Output
```
============================================================
  AI RESEARCH AGENT -- Rule-Based Orchestration
============================================================
  Question: What are the benefits of renewable energy?
============================================================

  [Step  1] Validating research question...
  [Step  1] Question accepted: 'What are the benefits of renewable energy?'
  [Step  2] Creating research plan...
  [Step  2]   * Search the web for: 'What are the benefits of renewable energy?'
  [Step  2]   * Retrieve and validate top search results
  [Step  2]   * Fetch full webpage content from validated URLs
  [Step  2]   * Extract and clean readable text from pages
  [Step  2]   * Rank evidence by keyword relevance to the question
  [Step  2]   * Compile findings into a structured report with source attribution
  [Step  2]   * Assess confidence based on evidence quantity and quality
  [Step  3] Selecting research tools...
  [Step  3]   Tool 1: Web Search (DuckDuckGo)
  [Step  3]   Tool 2: Web Scraper (BeautifulSoup)
  [Step  4] Executing web search...
  [Step  4] Search returned 5 results
  [Step  5] Validating and filtering search results...
  [Step  5] 5 results passed validation
  [Step  6] Fetching and extracting webpage content...
  [Step  6]   Fetching [1/5]: https://www.ucs.org/resources/benefits-renewable-energy-use
  [Step  6]   Fetching [2/5]: https://energydigital.com/top10/top-10-benefits-of-renewable-energy
  [Step  6]   Fetching [3/5]: https://greenlifezen.com/advantages-of-renewable-energy/
  [Step  6]   Fetching [4/5]: https://www.avaada.com/blog/advantages-and-importance-renewable-energy/
  [Step  6]   Fetching [5/5]: https://www.un.org/en/climatechange/raising-ambition/renewable-energy
  [Step  7] Ranking and filtering evidence...
  [Step  7] 5 findings after ranking
  [Step  8] Associating findings with source URLs...
  [Step  8]   -> https://www.avaada.com/blog/advantages-and-importance-renewable-energy/
  [Step  8]   -> https://www.ucs.org/resources/benefits-renewable-energy-use
  [Step  8]   -> https://energydigital.com/top10/top-10-benefits-of-renewable-energy
  [Step  8]   -> https://greenlifezen.com/advantages-of-renewable-energy/
  [Step  8]   -> https://www.un.org/en/climatechange/raising-ambition/renewable-energy
  [Step  9] Generating structured research report...
  [Step 10] Estimating evidence strength...
  [Step 10] Confidence: High -- Confidence is High. Based on: 5 pages had extractable content; average keyword relevance: 67%; 5 unique sources. (Heuristic score: 5/5)
  [Step 11] Identifying limitations and next steps...
  [Step 12] Recording execution log...
  [Step 12] Total execution time: 8.34s
  [Step 13] Assembling final report...

============================================================
  RESEARCH REPORT
============================================================

QUESTION: What are the benefits of renewable energy?

SHORT ANSWER:
  Based on 5 source(s), here is what was found: Renewable Energy | Top 10 Benefits for the Future Skip to content Advantages And Importance Of Renewable Energy By Pooja Patwari September 13, 2023 By Pooja Patwari September 13, 2023 Renewable energy is great for the environment and people. (Source: Renewable Energy | Top 10 Benefits for the Future)

CONFIDENCE: High
  Confidence is High. Based on: 5 pages had extractable content; average keyword relevance: 67%; 5 unique sources. (Heuristic score: 5/5)

KEY FINDINGS (5 source(s)):
------------------------------------------------------------

  Finding 1:
    Title:      Renewable Energy | Top 10 Benefits for the Future
    URL:        https://www.avaada.com/blog/advantages-and-importance-renewable-energy/
    Type:       Extracted webpage content
    Relevance:  100%
    Preview:    Renewable Energy | Top 10 Benefits for the Future Skip to content Advantages And Importance Of Renewable Energy By Pooja Patwari September 13, 2023...

[...Additional findings 2 through 5...]

LIMITATIONS:
  - This is a rule-based research agent without an LLM. It uses keyword matching for relevance â€” it cannot deeply understand or synthesize information the way a language model would.
  - Results are limited to what DuckDuckGo returns and what can be extracted from public HTML pages. Paywalled, JavaScript-rendered, or dynamic content may be inaccessible.
  - Confidence estimation uses a simple heuristic based on source count, keyword relevance, and content extraction success â€” not statistical analysis or expert evaluation.

SUGGESTED NEXT STEPS:
  - Verify key findings by visiting the original source URLs directly.
  - Cross-reference findings with academic databases or authoritative sources.
  - Narrow the research question for more targeted results.
  - Consider integrating an LLM for deeper synthesis and summarization.

Execution time: 8.34s
Sources: 5 searched -> 5 validated -> 5 extracted
============================================================
```

---

## 10. How Source Attribution Works

Source attribution is guaranteed through strict data lineage:
1. Every candidate result returned by `WebSearchTool` carries a `title`, `url`, and `snippet`.
2. When `WebScraperTool` extracts content from that URL, the data record is tagged with the exact URL and extracted title.
3. If web extraction fails, the search snippet is retained and labeled as `Evidence Type: Search snippet`.
4. During report generation, every finding displays its origin URL, source title, evidence type, and keyword relevance.
5. In accordance with assignment constraints, the system **never invents URLs, citations, or titles**. If an external resource cannot be accessed, it is marked as such.

---

## 11. How Confidence is Estimated

Rather than generating an arbitrary probability percentage, the agent applies an **explicit, deterministic heuristic scoring model** evaluated on a 5-point scale:

$$\text{Total Score} = S_{\text{extraction}} + S_{\text{relevance}} + S_{\text{diversity}}$$

### Scoring Breakdown
1. **Content Extraction Success ($S_{\text{extraction}}$)**:
   - $\ge 3$ full web pages extracted: **+2 points**
   - $1 - 2$ web pages extracted: **+1 point**
   - $0$ web pages extracted (snippets only): **0 points**
2. **Keyword Relevance ($S_{\text{relevance}}$)**:
   - Average keyword overlap $\ge 50\%$: **+2 points**
   - Average keyword overlap between $25\%$ and $49\%$: **+1 point**
   - Average keyword overlap $< 25\%$: **0 points**
3. **Source Diversity ($S_{\text{diversity}}$)**:
   - $\ge 3$ unique root domains/URLs: **+1 point**
   - $< 3$ unique sources: **0 points**

### Mapping to Confidence Levels
- **High**: Score of 4 or 5 (Requires multiple successfully extracted pages, strong keyword alignment, and diverse sources).
- **Moderate**: Score of 2 or 3 (Partial extraction success or moderate relevance).
- **Low**: Score of 0 or 1, or any query where average keyword relevance is 0% (e.g., gibberish or unresolvable questions).

---

## 12. Error-Handling & Security Measures

### Security Measures
- **SSRF Protection (`utils.is_safe_url`)**: Inspects every candidate URL. Rejects non-HTTP schemes (`file://`, `ftp://`, `javascript:`), loopback targets (`localhost`, `127.0.0.1`, `::1`), and private/reserved IPv4 addresses (e.g., `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- **Content-Type Enforcement**: Checks HTTP response headers before reading payloads; rejects binary files, PDFs, and non-HTML media.
- **Payload Size Caps**: Downloads are limited to 1 MB per request to mitigate decompression bombs and memory exhaustion.
- **Untrusted HTML Sanitization**: Strips executable script tags (`<script>`) and stylesheets (`<style>`) before text extraction to prevent prompt injection or script execution.

### Error-Handling Safeguards
- **HTTP Timeouts**: Fetch operations enforce a strict 10-second timeout; search enforces a 25-second timeout.
- **Graceful HTTP Error Fallback**: Catches HTTP 403, 404, and 500 errors. Automatically falls back to the search snippet for that source, ensuring reports complete even when individual pages block scrapers.
- **Windows Encoding Safeguards**: Automatically reconfigures terminal stdout to UTF-8 and uses ASCII fallback printing to prevent `UnicodeEncodeError` exceptions on Windows consoles using legacy `cp1252` code pages.

---

## 13. Why This Approach Was Chosen

1. **Deterministic & Testable**: Rule-based orchestration can be 100% covered by deterministic unit tests without flaky stochastic behavior.
2. **Zero Operating Cost**: Eliminates API key dependencies, usage billing, and token quotas. Anyone can clone and run the project immediately.
3. **Auditability**: Evaluators can inspect the exact logic governing tool execution, filtering, and scoring in pure Python standard libraries.
4. **Architectural Modularity**: Tools, utilities, and agent logic are decoupled. Replacing keyword extraction with an LLM synthesizer requires modifying only a single function in `research_agent.py`.

---

## 14. Limitations & Trade-Offs

- **No Semantic Synthesis**: The agent extracts literal text sentences matching query keywords. It does not perform semantic reasoning, paraphrase complex ideas, or draw deep multi-hop inferences like an LLM.
- **JavaScript-Rendered Content**: Pages relying on client-side SPA rendering (React/Vue/Angular) may return empty initial HTML when scraped via `requests`.
- **Bot Detection & Paywalls**: High-security commercial sites (e.g., Cloudflare-protected or paywalled news publications) may return HTTP 403 Forbidden errors, falling back to snippets.

---

## 15. Production-Readiness Gaps

If deploying this architecture into high-throughput production, the following enhancements should be implemented:
1. **Asynchronous I/O**: Migrating `requests` and `tools.py` to `httpx` or `aiohttp` to fetch multiple candidate pages concurrently via `asyncio`.
2. **Headless Browser Scraping**: Incorporating Playwright or Puppeteer for JavaScript-heavy or dynamic web applications.
3. **DNS Re-resolution Pinning**: Mitigating DNS rebinding attacks by verifying resolved IP addresses immediately prior to socket connection.
4. **Persistent Caching**: Storing retrieved search results and page hashes in Redis to reduce redundant external requests.

---

## 16. Monitoring, Logging, Latency & Cost

- **Latency Tracking**: End-to-end execution latency is measured via `time.time()` and recorded in every report. Typical queries complete in 7â€“13 seconds.
- **Structured Logging**: Uses Python's standard `logging` library. Secret masking and URL redaction can be hooked into log formatters.
- **Cost Considerations**:
  - **Current Cost**: $0.00 (Zero paid APIs, open-source dependencies).
  - **Projected LLM Cost (if integrated)**: Using an open-source model (e.g., via Ollama/vLLM) costs $0 in API fees, requiring ~4GB VRAM. Using paid APIs (e.g., Claude 3.5 Sonnet or GPT-4o-mini) would cost approximately $0.001 â€“ $0.003 per synthesized research report.

---

## 17. Future Improvements (Including Optional LLM Integration)

Because the project is built with clean separation of concerns, integrating a Large Language Model is straightforward:
1. **Abstractive Synthesis**: Pass the ranked findings into an LLM prompt to generate a cohesive multi-paragraph synthesis with in-text numerical citations (e.g., `[1]`, `[2]`).
2. **Query Reformulation**: Allow an LLM to generate 3 diverse search queries for complex topics.
3. **Streamlit UI**: Add an interactive browser interface with collapsible execution steps and exportable Markdown/PDF reports.

---

## 18. Core Assignment Questions Answered

To directly address the specific requirements outlined in the assignment specification:

| Question from Specification | Architecture & Design Decision |
|---|---|
| **Why did you choose an agentic approach here?** | Rather than a single static API call or keyword search, complex research requires iterative decomposition: validating the question, selecting appropriate tools dynamically, recovering when individual pages fail or block access, and synthesizing multi-source findings into a structured schema. |
| **What tools did you use, and why?** | We integrated two complementary tools: `WebSearchTool` via DuckDuckGo (`ddgs`) for free, broad query discovery without API keys, and `WebScraperTool` via `requests` and `BeautifulSoup4` for targeted full-DOM HTML retrieval and script-stripped text extraction. |
| **How does the system handle bad tool results?** | When search fails or yields zero hits, the agent catches the error and reports an honest explanation. When webpage scraping encounters HTTP errors (403, 404, 500) or timeouts, it automatically logs the incident and falls back to using the search engine's snippet as an alternate evidence record. |
| **How do you reduce hallucinations?** | The system enforces strict citation lineage: every finding is bound to a verified source URL and extracted title. The agent never invents citations, and when evidence has 0% keyword match, it rejects the findings and explicitly reports that no reliable evidence could be located. |
| **How would you make this production-ready?** | By migrating HTTP scraping to asynchronous I/O (`httpx` / `aiohttp`), integrating headless browser rendering (Playwright) for JavaScript SPAs, adding distributed caching (Redis), and implementing strict DNS re-resolution pinning against rebinding attacks. |
| **What would you monitor in production?** | End-to-end query latency, search engine error rates, scraping success/timeout percentages, average relevance scores, confidence level distributions, and memory usage per request. |
| **What were your key tradeoffs?** | We chose a deterministic, rule-based keyword relevance approach over an LLM API to guarantee 100% testability, zero operating cost, no API rate limits, and elimination of non-deterministic hallucinations. The trade-off is that answer synthesis relies on extracted text rather than generative abstractive summarization. |

---

## 19. Transparent LLM Disclosure

> [!IMPORTANT]
> **Transparent Disclosure**: This implementation is strictly a **rule-based autonomous agent** utilizing explicit Python orchestration, deterministic keyword relevance ranking, and transparent heuristic confidence estimation. **No Large Language Model (LLM) or paid AI API is used in this core codebase.** This deliberate architecture ensures complete transparency, zero financial dependency, full reproducibility, and robust interview-ready explainability.

