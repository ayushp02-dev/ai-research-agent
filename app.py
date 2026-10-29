"""
AI Research Agent — Streamlit Interactive Web Application.

An enterprise-grade, interview-ready research platform featuring:
- Autonomous 13-step orchestration with live progress streaming
- Rich interactive Plotly visualizations (Relevance rankings, Confidence gauge, Retrieval funnel, Domain distribution)
- In-App Documentation & Architecture Explorer (README, Evaluation report, Demo script)
- Research session history & multi-query comparison
- Keyword highlighter in evidence previews
- Multi-format report export (Styled HTML, Markdown, JSON)
"""

import json
import os
import re
import time
from urllib.parse import urlparse

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from research_agent import STOP_WORDS, ResearchAgent

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Custom Styling (Glassmorphism & Modern Aesthetic)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border: 1px solid #e2e8f0;
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0f172a;
    }

    /* Executive Summary Card */
    .summary-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.08);
    }

    /* Evidence Finding Card */
    .finding-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .finding-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.06);
        border-color: #38bdf8;
    }

    /* Badges */
    .badge-high {
        background: #dcfce7;
        color: #166534;
        padding: 5px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.82rem;
        display: inline-block;
        border: 1px solid #86efac;
    }
    .badge-moderate {
        background: #fef9c3;
        color: #854d0e;
        padding: 5px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.82rem;
        display: inline-block;
        border: 1px solid #fde047;
    }
    .badge-low {
        background: #fee2e2;
        color: #991b1b;
        padding: 5px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.82rem;
        display: inline-block;
        border: 1px solid #fca5a5;
    }
    .badge-source {
        background: #f1f5f9;
        color: #334155;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid #cbd5e1;
    }
    .badge-domain {
        background: #eff6ff;
        color: #1d4ed8;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid #bfdbfe;
    }

    /* Keyword Highlight */
    mark.highlight {
        background-color: #fef08a;
        color: #854d0e;
        padding: 2px 4px;
        border-radius: 4px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def get_domain(url):
    """Extract clean domain name from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    except Exception:
        return "external"


def highlight_keywords(text, question):
    """Highlight query keywords within the extracted text snippet."""
    if not text or not question:
        return text

    q_words = set(re.findall(r"\b\w+\b", question.lower()))
    keywords = [w for w in q_words if w not in STOP_WORDS and len(w) > 2]

    if not keywords:
        return text

    # Case-insensitive replacement with <mark> tags
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in keywords) + r")\b", re.IGNORECASE)
    highlighted = pattern.sub(r'<mark class="highlight">\1</mark>', text)
    return highlighted


def load_file_content(relative_path):
    """Safely load local project files for in-app documentation explorer."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(base_dir, relative_path)
    if os.path.exists(target):
        with open(target, "r", encoding="utf-8") as f:
            return f.read()
    return f"File not found: {relative_path}"


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state["history"] = []

if "current_report" not in st.session_state:
    st.session_state["current_report"] = None

# -----------------------------------------------------------------------------
# Sidebar Configuration & Parameters
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔬 AI Research Agent")
    st.caption("Autonomous Research Platform")
    st.markdown("---")

    st.markdown("#### ⚙️ Research Controls")
    max_results = st.slider(
        "Max Search Results",
        min_value=3,
        max_value=8,
        value=5,
        help="Number of web sources to query and extract.",
    )

    domain_filter = st.text_input(
        "Domain Filter (Optional)",
        placeholder="e.g. org, edu, wikipedia.org",
        help="Optional domain keyword or TLD to prioritize.",
    )

    st.markdown("---")
    st.markdown("#### 💡 Quick Test Presets")
    st.caption("Click to load verified benchmark questions:")

    test_queries = [
        ("🌱 Renewable Energy", "What are the benefits of renewable energy?"),
        ("🌿 Photosynthesis (403 Test)", "How does photosynthesis work?"),
        ("⚛️ Quantum Computing", "What are the latest developments in quantum computing?"),
        ("❌ Negative Query Test", "xyzabcqwerty9876543210nonexistentquery"),
    ]

    for label, q_text in test_queries:
        if st.button(label, key=f"btn_{label}"):
            st.session_state["active_query"] = q_text

    st.markdown("---")
    st.markdown("#### 🛡️ Verified Safeguards")
    st.markdown(
        """
        - 🔒 **SSRF Protection** (Blocks private IPs & localhost)
        - 📑 **Content-Type Filter** (Strict HTML validation)
        - ⏱️ **Timeout Caps** (10s scrape / 25s search)
        - 🌐 **100% Verifiable URLs** (No fake citations)
        - 🧪 **23/23 Tests Passed** (`pytest` passing)
        """
    )

    st.markdown("---")
    st.caption("Deterministic Rule-Based Agent • No Paid APIs")

# -----------------------------------------------------------------------------
# Main Hero Section
# -----------------------------------------------------------------------------
st.title("🔬 AI Research Agent")
st.markdown(
    "**Autonomous Rule-Based Information Retrieval & Visual Synthesis Platform**  \n"
    "*Built with Python, DuckDuckGo (`ddgs`), BeautifulSoup4, and Plotly*"
)

st.markdown(
    """
    <div style="display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap;">
        <span class="badge-source">⚡ DuckDuckGo Engine</span>
        <span class="badge-source">🛡️ SSRF Protected</span>
        <span class="badge-source">🌐 BeautifulSoup Scraper</span>
        <span class="badge-source">📊 Plotly Visualizations</span>
        <span class="badge-source">🧪 23 Automated Tests</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Query Input & Action Bar
# -----------------------------------------------------------------------------
initial_query = st.session_state.get("active_query", "What are the benefits of renewable energy?")

query_input = st.text_input(
    "Research Question:",
    value=initial_query,
    placeholder="Ask any research question (e.g. How does photosynthesis work?)...",
)

col_run, col_clear, _ = st.columns([1.5, 1.2, 5])
with col_run:
    run_btn = st.button("🚀 Run Research", type="primary", use_container_width=True)

with col_clear:
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state["history"] = []
        st.session_state["current_report"] = None
        st.rerun()

# -----------------------------------------------------------------------------
# Live Orchestration Execution
# -----------------------------------------------------------------------------
if run_btn:
    if not query_input.strip():
        st.error("⚠️ Please provide a non-empty research question.")
    else:
        # Live progress container
        status_box = st.status("🤖 Orchestrating 13-Step Research Pipeline...", expanded=True)

        step_icons = {
            1: "📋", 2: "🗺️", 3: "🛠️", 4: "🔍", 5: "🛡️",
            6: "🌐", 7: "📊", 8: "🔗", 9: "📑", 10: "⚖️",
            11: "⚠️", 12: "⏱️", 13: "✅",
        }

        def stream_step(step_num, message):
            icon = step_icons.get(step_num, "🔹")
            status_box.write(f"{icon} **Step {step_num}**: {message}")

        agent = ResearchAgent(
            max_search_results=max_results,
            verbose=False,
            step_callback=stream_step,
        )

        effective_query = query_input.strip()
        if domain_filter.strip():
            effective_query = f"{effective_query} site:{domain_filter.strip()}"

        report = agent.research(effective_query)

        status_box.update(
            label=f"✅ Research Completed in {report['execution_time_seconds']}s!",
            state="complete",
            expanded=False,
        )

        # Store in session state and history
        st.session_state["current_report"] = report
        st.session_state["history"].append({
            "timestamp": time.strftime("%H:%M:%S"),
            "query": query_input.strip(),
            "report": report,
        })

# -----------------------------------------------------------------------------
# Research Session History Selector (Multi-Query Switcher)
# -----------------------------------------------------------------------------
if st.session_state["history"]:
    st.markdown("---")
    st.markdown("#### 📂 Research Session History")
    hist_cols = st.columns(min(len(st.session_state["history"]), 4))
    for idx, item in enumerate(reversed(st.session_state["history"][-4:])):
        with hist_cols[idx]:
            label = f"🕒 {item['timestamp']}: {item['query'][:22]}..."
            if st.button(label, key=f"hist_{idx}", use_container_width=True):
                st.session_state["current_report"] = item["report"]
                st.rerun()

# -----------------------------------------------------------------------------
# Report Presentation & Visualizations
# -----------------------------------------------------------------------------
if st.session_state["current_report"]:
    rep = st.session_state["current_report"]
    conf = rep["confidence"]
    findings = rep["findings"]

    st.markdown("---")
    st.subheader("📑 Research Synthesis & Analytics")

    # 1. Top Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Execution Latency",
            value=f"{rep['execution_time_seconds']}s",
            help="Total time taken for search, safety validation, scraping, and ranking.",
        )
    with m2:
        conf_level = conf["level"]
        badge_cls = (
            "badge-high" if conf_level == "High"
            else "badge-moderate" if conf_level == "Moderate"
            else "badge-low"
        )
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 14px 18px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase;">Confidence Level</div>
                <div style="margin-top: 6px;"><span class="{badge_cls}">{conf_level.upper()}</span> <small style="color: #64748b;">({conf.get('score', 0)}/5 pts)</small></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.metric(
            label="Source Extraction Ratio",
            value=f"{rep['sources_extracted']} / {rep['sources_validated']}",
            help="Webpages successfully scraped vs total safe URLs validated.",
        )
    with m4:
        avg_rel = (
            sum(f["relevance_score"] for f in findings) / len(findings)
            if findings else 0.0
        )
        st.metric(
            label="Average Relevance",
            value=f"{avg_rel:.0%}",
            help="Average keyword match density across all retrieved evidence.",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Executive Short Answer Card
    st.markdown(
        f"""
        <div class="summary-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="margin: 0; color: #0284c7; font-size: 1.25rem;">Executive Short Answer</h3>
                <span class="{badge_cls}">Confidence: {conf_level}</span>
            </div>
            <p style="font-size: 1.1rem; line-height: 1.6; color: #0f172a; margin-bottom: 14px;">
                {rep['short_answer']}
            </p>
            <div style="font-size: 0.85rem; color: #475569; background: rgba(255,255,255,0.6); padding: 8px 12px; border-radius: 8px;">
                <strong>Confidence Evaluation Heuristic:</strong> {conf['explanation']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Interactive Analytics & Visualizations Section
    st.markdown("### 📊 Interactive Visual Analytics")

    vcol1, vcol2 = st.columns([3, 2])

    with vcol1:
        st.markdown("##### Source Relevance & Evidence Quality")
        if findings:
            chart_data = []
            for f in findings:
                domain = get_domain(f["source_url"])
                title_short = (f["source_title"][:28] + "..") if len(f["source_title"]) > 28 else f["source_title"]
                chart_data.append({
                    "Source": f"{title_short} ({domain})",
                    "Relevance": f["relevance_score"] * 100,
                    "Evidence Type": f["evidence_type"],
                    "URL": f["source_url"],
                })
            df_chart = pd.DataFrame(chart_data)

            fig_bar = px.bar(
                df_chart,
                x="Relevance",
                y="Source",
                orientation="h",
                color="Evidence Type",
                color_discrete_map={
                    "Extracted webpage content": "#0284c7",
                    "Search snippet": "#f59e0b",
                },
                labels={"Relevance": "Relevance Match (%)"},
                text="Relevance",
            )
            fig_bar.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
            fig_bar.update_layout(
                yaxis={"autorange": "reversed"},
                margin={"l": 20, "r": 20, "t": 10, "b": 20},
                height=280,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No sources met the relevance threshold for charting.")

    with vcol2:
        st.markdown("##### Confidence Heuristic Gauge (0–5 pts)")
        total_score = conf.get("score", 0)

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=total_score,
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 5], "tickwidth": 1, "tickcolor": "#475569"},
                    "bar": {"color": "#0284c7"},
                    "bgcolor": "white",
                    "steps": [
                        {"range": [0, 2], "color": "#fee2e2"},
                        {"range": [2, 4], "color": "#fef9c3"},
                        {"range": [4, 5], "color": "#dcfce7"},
                    ],
                    "threshold": {
                        "line": {"color": "#16a34a", "width": 4},
                        "thickness": 0.75,
                        "value": 4.0,
                    },
                },
            )
        )
        fig_gauge.update_layout(
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
            height=200,
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Component breakdown pills
        c_ext = conf.get("extracted_score", 0)
        c_rel = conf.get("relevance_score", 0)
        c_div = conf.get("diversity_score", 0)
        st.caption(
            f"**Heuristic Breakdown:** Extracted Content: **+{c_ext}** | "
            f"Keyword Relevance: **+{c_rel}** | "
            f"Domain Diversity: **+{c_div}**"
        )

    # 4. Pipeline Retrieval Funnel
    st.markdown("##### Information Retrieval Funnel")
    funnel_stages = ["1. Searched", "2. Validated Safe", "3. Extracted", "4. Top Relevant"]
    funnel_values = [
        rep["sources_searched"],
        rep["sources_validated"],
        rep["sources_extracted"],
        len(findings),
    ]

    fig_funnel = go.Figure(
        go.Funnel(
            y=funnel_stages,
            x=funnel_values,
            textinfo="value+percent initial",
            marker={"color": ["#64748b", "#3b82f6", "#0284c7", "#10b981"]},
        )
    )
    fig_funnel.update_layout(
        margin={"l": 20, "r": 20, "t": 10, "b": 10},
        height=190,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

    # -------------------------------------------------------------------------
    # Report Tabs
    # -------------------------------------------------------------------------
    st.markdown("---")
    tab_findings, tab_transparency, tab_log, tab_docs, tab_export = st.tabs(
        [
            f"🔍 Key Findings ({len(findings)})",
            "⚖️ Limitations & Next Steps",
            "📜 13-Step Execution Log",
            "📖 In-App Documentation Explorer",
            "📦 Report Export Options",
        ]
    )

    # TAB 1: Key Findings with Keyword Highlighting
    with tab_findings:
        if not findings:
            st.warning("No findings passed the relevance threshold. Try rephrasing your research query.")
        else:
            for i, f in enumerate(findings, 1):
                domain = get_domain(f["source_url"])
                highlighted_excerpt = highlight_keywords(f["text"][:400], rep["question"])

                st.markdown(
                    f"""
                    <div class="finding-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                            <div>
                                <span class="badge-domain">🌐 {domain}</span>
                                <h4 style="margin: 6px 0 0 0; font-size: 1.1rem;">
                                    Finding {i}: <a href="{f['source_url']}" target="_blank" style="text-decoration: none; color: #0284c7;">{f['source_title']}</a>
                                </h4>
                            </div>
                            <span class="badge-source">{f['evidence_type']}</span>
                        </div>
                        <div style="margin: 8px 0;">
                            <span style="font-size: 0.85rem; color: #475569;">
                                <strong>Relevance Density:</strong> {f['relevance_score']:.0%} match
                            </span>
                        </div>
                        <div style="background: #f8fafc; border-left: 3px solid #0284c7; padding: 12px 14px; border-radius: 6px; font-size: 0.95rem; line-height: 1.6; color: #334155; margin-bottom: 8px;">
                            "{highlighted_excerpt}{'...' if len(f['text']) > 400 else ''}"
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #64748b;">
                            <span>Source: <a href="{f['source_url']}" target="_blank" style="color: #64748b;">{f['source_url']}</a></span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander(f"📄 View Full Extracted Text for Finding {i}"):
                    st.write(f["text"])

    # TAB 2: Limitations & Next Steps
    with tab_transparency:
        col_l, col_n = st.columns(2)
        with col_l:
            st.markdown("#### ⚠️ Documented Limitations")
            for lim in rep["limitations"]:
                st.markdown(f"- {lim}")
        with col_n:
            st.markdown("#### 🧭 Suggested Next Steps")
            for step in rep["next_steps"]:
                st.markdown(f"- {step}")

    # TAB 3: Execution Log
    with tab_log:
        st.markdown("#### 📜 Verifiable Execution Audit Trail")
        st.caption("Deterministic log generated step-by-step during this execution:")
        st.code("\n".join(rep["execution_log"]), language="text")

    # TAB 4: In-App Documentation Explorer (README, Evaluation, Demo Script)
    with tab_docs:
        st.markdown("#### 📖 Project Documentation & Benchmark Files")
        doc_choice = st.radio(
            "Select Documentation File to View:",
            ["README.md", "Evaluation Report (5 Benchmark Tests)", "3–5 Min Demo Script & Checklist"],
            horizontal=True,
        )

        if doc_choice == "README.md":
            readme_content = load_file_content("README.md")
            st.markdown(readme_content)
        elif doc_choice == "Evaluation Report (5 Benchmark Tests)":
            eval_content = load_file_content("evaluation/evaluation_report.md")
            st.markdown(eval_content)
        else:
            demo_content = load_file_content("demo/demo_script.md")
            st.markdown(demo_content)

    # TAB 5: Report Export Options
    with tab_export:
        st.markdown("#### 📦 Multi-Format Report Export")
        st.caption("Export your research report directly to JSON, Markdown, or styled HTML:")

        # Prepare formats
        json_export = json.dumps(rep, indent=2, ensure_ascii=False)

        md_export = f"""# Research Report: {rep['question']}

**Execution Time:** {rep['execution_time_seconds']}s  
**Confidence Level:** {conf['level']}  
**Confidence Rationale:** {conf['explanation']}  

---

## Executive Short Answer
{rep['short_answer']}

---

## Key Findings ({len(findings)} sources)
"""
        for i, f in enumerate(findings, 1):
            md_export += f"""
### Finding {i}: [{f['source_title']}]({f['source_url']})
- **Evidence Type:** {f['evidence_type']}
- **Relevance Score:** {f['relevance_score']:.0%}
- **Source URL:** {f['source_url']}
- **Excerpt:**
> {f['text'][:350]}...

"""

        md_export += """
---

## Documented Limitations
"""
        for l in rep["limitations"]:
            md_export += f"- {l}\n"

        md_export += """
## Suggested Next Steps
"""
        for s in rep["next_steps"]:
            md_export += f"- {s}\n"

        # HTML Export
        html_export = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Research Report: {rep['question']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 850px; margin: 40px auto; padding: 20px; line-height: 1.6; color: #1e293b; }}
        h1 {{ color: #0f172a; border-bottom: 2px solid #0284c7; padding-bottom: 8px; }}
        .badge {{ background: #0284c7; color: white; padding: 4px 10px; border-radius: 9999px; font-weight: bold; font-size: 0.85rem; }}
        .summary {{ background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 18px; margin: 20px 0; }}
        .finding {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
        blockquote {{ border-left: 3px solid #0284c7; margin: 0; padding-left: 12px; color: #475569; }}
    </style>
</head>
<body>
    <h1>🔬 AI Research Agent Report</h1>
    <p><strong>Question:</strong> {rep['question']}</p>
    <p><strong>Latency:</strong> {rep['execution_time_seconds']}s | <span class="badge">Confidence: {conf['level']}</span></p>
    
    <div class="summary">
        <h3>Executive Short Answer</h3>
        <p>{rep['short_answer']}</p>
        <small>{conf['explanation']}</small>
    </div>

    <h2>Key Findings ({len(findings)})</h2>
"""
        for i, f in enumerate(findings, 1):
            html_export += f"""
    <div class="finding">
        <h4>Finding {i}: <a href="{f['source_url']}">{f['source_title']}</a></h4>
        <p><strong>Type:</strong> {f['evidence_type']} | <strong>Relevance:</strong> {f['relevance_score']:.0%}</p>
        <blockquote>"{f['text'][:300]}..."</blockquote>
        <p><small>URL: {f['source_url']}</small></p>
    </div>
"""
        html_export += """
</body>
</html>"""

        exp_c1, exp_c2, exp_c3 = st.columns(3)
        with exp_c1:
            st.download_button(
                label="📥 Download JSON Report",
                data=json_export,
                file_name=f"research_report_{int(time.time())}.json",
                mime="application/json",
                use_container_width=True,
            )
        with exp_c2:
            st.download_button(
                label="📥 Download Markdown Report",
                data=md_export,
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with exp_c3:
            st.download_button(
                label="📥 Download HTML Report",
                data=html_export,
                file_name=f"research_report_{int(time.time())}.html",
                mime="text/html",
                use_container_width=True,
            )
