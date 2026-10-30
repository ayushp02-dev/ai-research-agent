# AI Research Agent â€” Demo Script & Submission Guide

This document provides a complete, step-by-step 3â€“5 minute demonstration script for presenting the **AI Research Agent** project during an interview or demo video, followed by the complete submission checklist and GitHub publishing instructions.

---

## Part 1: 3â€“5 Minute Demo Script

### Demo Overview & Setup
- **Goal**: Demonstrate input validation, planning, tool usage (search & scraper), evidence ranking, source attribution, failure resilience, and test suite execution.
- **Environment**: Windows Terminal / PowerShell in the project directory:
  ```powershell
  cd C:\Users\ayush\ai-research-agent
  ```

---

### Segment 1: Introduction & Architecture Overview (0:00 â€“ 0:45)
**What to say:**
> "Hello! Today I am presenting my AI Research Agent project.
> The agent is designed to take an open-ended research question, create an execution plan, use two distinct external toolsâ€”DuckDuckGo web search and a BeautifulSoup-based web scraperâ€”filter and rank retrieved evidence, and produce a structured research report with complete source attribution, confidence estimation, and limitation disclosures.
> Crucially, this implementation is an honest, rule-based autonomous agent without relying on paid or black-box LLM APIs. Its modular design allows seamless integration of LLMs later for synthesis, while maintaining strict security safeguards against SSRF and untrusted web content."

---

### Segment 2: Standard Research Workflow Execution (0:45 â€“ 2:00)
**Action:**
Run a standard research query from the command line:
```powershell
python main.py "What are the benefits of renewable energy?"
```

**What to highlight on screen as output scrolls:**
1. **Input Validation (Step 1)**: The agent verifies the query is non-empty and well-formed.
2. **Visible Planning (Step 2)**: The agent generates and prints a 7-step research plan.
3. **Tool Selection (Step 3)**: Explicit selection of `Tool 1: Web Search (DuckDuckGo)` and `Tool 2: Web Scraper (BeautifulSoup)`.
4. **Tool 1 Execution & Filtering (Steps 4 & 5)**: Queries search engine, validates URLs for safety (blocking localhost and private IPs), and filters malformed results.
5. **Tool 2 Execution (Step 6)**: Fetches verified web pages, enforces timeouts and size limits, strips scripts/styles, and extracts readable text.
6. **Ranking & Attribution (Steps 7 & 8)**: Ranks evidence by query keyword relevance and maps every finding to its original source URL.
7. **Confidence & Limitations (Steps 10 & 11)**: Computes confidence using a transparent heuristic (source count, keyword relevance, page extraction success) rather than an invented probability.

---

### Segment 3: Error & Edge-Case Handling (2:00 â€“ 3:00)
**Action 1 (Empty Input Validation):**
```powershell
python main.py ""
```
*Point out:* The agent immediately catches empty input, issues an explanation, and sets confidence to Low without crashing or making unnecessary network calls.

**Action 2 (Non-Existent / Obscure Query):**
```powershell
python main.py "xyzabcqwerty9876543210nonexistentquery"
```
*Point out:* When search yields 0 results, the agent handles the outcome gracefully, explicitly reporting that no reliable evidence could be located, rather than hallucinating findings.

---

### Segment 4: Automated Test Suite (3:00 â€“ 3:45)
**Action:**
Run the complete test suite:
```powershell
pytest tests/ -v
```

**What to point out:**
- 23 automated unit and integration tests run in under 2 seconds.
- 100% offline and deterministic: all network calls (DuckDuckGo and HTTP requests) are mocked.
- Covers all edge cases:
  - Network timeouts and HTTP error codes (404, 500)
  - Unsafe URL rejections (SSRF / localhost / private IPs)
  - Content-Type filtering (blocking non-HTML files like PDFs)
  - HTML script/style element sanitization
  - Report schema completeness and source attribution integrity

---

### Segment 5: Conclusion & Architecture Wrap-Up (3:45 â€“ 4:30)
**What to say:**
> "To summarize, the AI Research Agent provides a resilient, transparent, and modular research workflow.
> By implementing explicit orchestration, strict security validation, and deterministic confidence scoring, the platform remains safe and reliable.
> Thank you, and I look forward to your questions!"

---

## Part 2: Submission Checklist

Before submitting the assignment, ensure each of the following requirements is satisfied:

- [ ] **GitHub Repository**: Code pushed to a public GitHub repository.
- [ ] **README.md**: Complete documentation covering all 18 required sections.
- [ ] **Requirements File**: Clean `requirements.txt` with only necessary packages.
- [ ] **Gitignore**: Excludes `.venv`, `__pycache__`, and temporary files.
- [ ] **Automated Tests**: All 23 tests pass using `pytest tests/ -v`.
- [ ] **Evaluation Document**: `evaluation/evaluation_report.md` with 5 test queries and evaluation rubric.
- [ ] **Sample Outputs**: `examples/sample_outputs.md` containing real application runs.
- [ ] **No Paid API Dependency**: Verified zero dependency on OpenAI or paid keys.
- [ ] **Demo Video**: 3â€“5 minute screen recording following the demo script above.
- [ ] **AI Disclosure**: Transparent acknowledgment of AI coding assistance tools used during development.

---

## Part 3: GitHub Publication Guide (Windows)

Follow these exact steps in Windows PowerShell to publish this project to GitHub.

### Step 1: Initialize Git Repository
```powershell
cd C:\Users\ayush\ai-research-agent
git init
git status
```

### Step 2: Configure Git User (If not already set)
```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

### Step 3: Add Files and Commit
```powershell
git add .
git commit -m "feat: initial implementation of AI Research Agent with tools, tests, and documentation"
```

### Step 4: Create Repository on GitHub
1. Log in to your GitHub account at [github.com](https://github.com).
2. Click the **+** icon in the top-right corner and select **New repository**.
3. Repository name: `ai-research-agent` (or `ai-research-agent`).
4. Visibility: **Public**.
5. Do **NOT** check "Initialize this repository with a README" (we already created one).
6. Click **Create repository**.

### Step 5: Link Local Repo to GitHub and Push
```powershell
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/ai-research-agent.git
git push -u origin main
```
*(Enter your GitHub credentials or personal access token if prompted).*

