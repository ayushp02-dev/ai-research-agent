# AI Research Agent — Evaluation Report & Benchmark

This report documents the empirical evaluation of the **AI Research Agent**, testing the system across 5 representative research queries spanning factual science, contemporary technology, error handling, edge cases, and empty input validation.

All evaluation runs were conducted locally in the actual runtime environment with real network retrieval, real content extraction, and real error handling.

---

## 1. Evaluation Rubric

Each query is evaluated across five objective criteria:

| Criterion | Definition | Standard for "Pass" |
|---|---|---|
| **Source Relevance** | Degree to which retrieved URLs and text content match the core keywords and intent of the research query. | ≥ 50% average keyword relevance for valid queries; 0% relevance correctly detected for gibberish. |
| **Citation Correctness** | Every finding must link to its authentic source URL with valid HTTP/HTTPS protocol and verifiable page title. | 100% of reported findings have verifiable source URLs and titles; zero fabricated citations. |
| **Failure Handling** | Graceful recovery when external services fail (HTTP 403/404/500, timeouts, invalid input, zero results). | No unhandled exceptions; informative error messages logged; fallback to search snippet when scraping fails. |
| **Output Completeness** | Report adheres to the required schema: question, short answer, key findings, confidence, limitations, and next steps. | All required keys present and populated with non-trivial content. |
| **Response Time** | End-to-end execution latency from initial input to complete report generation. | ≤ 30 seconds per query under standard broadband connection. |

---

## 2. Test Queries & Empirical Results

### Query 1: Factual Science Query
- **Question**: `"What are the benefits of renewable energy?"`
- **Expected Behavior**: Search DuckDuckGo, validate safe URLs, scrape top pages, rank evidence, and produce a High-confidence report citing multiple independent environmental and energy sources.
- **Actual Observed Behavior**:
  - Sources searched: 5 | Validated: 5 | Scraped: 5 (100% extraction success rate)
  - Key sources: Avaada Energy, Union of Concerned Scientists, Energy Digital, GreenLifeZen, United Nations
  - Top relevance score: 100% (Avaada Energy), average relevance: 67%
  - Confidence: **High** (Heuristic score: 5/5)
  - Execution time: **8.34 seconds**
- **Status**: **PASS**
- **Remaining Limitation**: The short answer extracts the leading paragraph of the top finding rather than performing abstractive multi-source semantic summarization.

---

### Query 2: Educational Science with HTTP Error Handling
- **Question**: `"How does photosynthesis work?"`
- **Expected Behavior**: Retrieve scientific sources explaining light-dependent and dark reactions; gracefully handle paywalls or anti-bot blocks from major educational sites.
- **Actual Observed Behavior**:
  - Sources searched: 5 | Validated: 5 | Successfully scraped: 4
  - **Graceful Failure Tested**: `https://www.britannica.com/science/photosynthesis` returned an **HTTP 403 Forbidden** error. The agent caught the error, logged the failure, and automatically fell back to the DuckDuckGo search snippet for that source without halting execution.
  - Limitations field accurately recorded: *"1 webpage(s) could not be fetched or had insufficient content."*
  - Key sources: Sciencing.com, BBC Science Focus, Wikipedia, Encyclopaedia Britannica, Science News Explores
  - Confidence: **High** (Heuristic score: 5/5)
  - Execution time: **7.25 seconds**
- **Status**: **PASS**
- **Remaining Limitation**: Sites employing advanced Cloudflare or bot-management screens (like Britannica) require headless browser emulation (e.g., Playwright) for full DOM extraction.

---

### Query 3: Contemporary Technology Research
- **Question**: `"What are the latest developments in quantum computing?"`
- **Expected Behavior**: Retrieve contemporary articles and institutional reports on hardware, algorithms, and commercial developments in quantum computing.
- **Actual Observed Behavior**:
  - Sources searched: 5 | Validated: 5 | Scraped: 5 (100% extraction success rate)
  - Key sources: MIT News, Quantum Zeitgeist, Open Access Government, USDSI, ScienceDaily
  - Average keyword relevance: 50%
  - Confidence: **High** (Heuristic score: 5/5)
  - Execution time: **13.15 seconds**
- **Status**: **PASS**
- **Remaining Limitation**: Search results include recent news releases, but temporal verification (filtering strictly by publication date) is bounded by what metadata DuckDuckGo provides.

---

### Query 4: Obscure / Non-Existent Query (Negative Test)
- **Question**: `"xyzabcqwerty9876543210nonexistentquery"`
- **Expected Behavior**: When search engines return generic or off-target results with zero matching keywords, the agent must reject the findings, report Low confidence, and state that no reliable evidence could be located.
- **Actual Observed Behavior**:
  - Sources returned by search: 5 generic pages (matching partial substring "xyz")
  - Evidence ranking: Detected 0% keyword relevance across all candidate pages.
  - Zero-relevance filter: Correctly filtered out all 5 candidate pages (0 findings passed threshold).
  - Short answer: *"The research agent could not find sufficient evidence to answer this question. Please try rephrasing with more specific terms."*
  - Confidence: **Low** (*"No relevant findings matching the research query were retrieved."*)
  - Execution time: **10.87 seconds**
- **Status**: **PASS**
- **Remaining Limitation**: Query does not trigger an external spell-check or suggestion engine.

---

### Query 5: Empty Input Validation (Edge Case)
- **Question**: `""` (Empty string)
- **Expected Behavior**: Immediate input rejection at Step 1; zero network requests dispatched; informative error message; execution terminates in < 1 second.
- **Actual Observed Behavior**:
  - Step 1 caught empty string immediately.
  - Network requests dispatched: 0
  - Short answer: *"Research question is empty or invalid."*
  - Confidence: **Low** (*"Research question is empty or invalid."*)
  - Execution time: **0.00 seconds** (instantaneous)
- **Status**: **PASS**
- **Remaining Limitation**: None. Input validation functions deterministically.

---

## 3. Evaluation Summary Table

| # | Test Query | Sources Searched | Sources Extracted | Avg Relevance | Confidence | Latency | Result |
|---|---|---|---|---|---|---|---|
| 1 | Benefits of renewable energy | 5 | 5 | 67% | High | 8.34s | **PASS** |
| 2 | How does photosynthesis work? | 5 | 4 (1 HTTP 403 fallback) | 70% | High | 7.25s | **PASS** |
| 3 | Latest developments in quantum computing | 5 | 5 | 50% | High | 13.15s | **PASS** |
| 4 | xyzabcqwerty9876543210... (gibberish) | 5 | 0 passed filter | 0% | Low | 10.87s | **PASS** |
| 5 | "" (empty string) | 0 | 0 | N/A | Low | 0.00s | **PASS** |

**Overall Evaluation Score: 5/5 (100% Passed)**
