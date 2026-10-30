"""
AI Research Agent — Streamlit Interactive Web Application.

An enterprise-grade, interview-ready research platform featuring:
- Autonomous 13-step orchestration with live progress streaming
- High-aesthetic glassmorphism UI with ambient lighting and Google Fonts (Plus Jakarta Sans)
- Rich interactive Plotly visualizations (Relevance ranking, Confidence gauge, Retrieval funnel, Content depth)
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
# High-Aesthetic Glassmorphism & Modern CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Ambient background styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    /* Hero Branding */
    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 32px 36px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 380px;
        height: 380px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, rgba(99, 102, 241, 0.08) 50%, transparent 75%);
        pointer-events: none;
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 20%, #93c5fd 60%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.5;
        max-width: 820px;
        margin-bottom: 18px;
    }
    .hero-tags {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        align-items: center;
    }

    /* Live Pulsing Dot */
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 1.8s infinite;
        margin-right: 6px;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .badge-pill {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #e2e8f0;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 500;
        backdrop-filter: blur(8px);
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        padding: 18px 22px;
        border-radius: 16px;
        box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.04);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.08);
        border-color: #93c5fd;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.02em;
    }

    /* Executive Summary Card */
    .summary-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f0f9ff 50%, #eff6ff 100%);
        border: 1px solid #bae6fd;
        border-radius: 16px;
        padding: 26px 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(14, 165, 233, 0.08);
        position: relative;
    }
    .summary-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, #0284c7 0%, #6366f1 100%);
        border-top-left-radius: 16px;
        border-bottom-left-radius: 16px;
    }

    /* Evidence Finding Card */
    .finding-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .finding-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 24px -6px rgba(15, 23, 42, 0.08);
        border-color: #38bdf8;
    }

    /* Confidence Badges */
    .badge-high {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        color: #065f46;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.82rem;
        border: 1px solid #6ee7b7;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
    }
    .badge-moderate {
        background: linear-gradient(135deg, #fefce8 0%, #fef08a 100%);
        color: #854d0e;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.82rem;
        border: 1px solid #fde047;
        box-shadow: 0 2px 4px rgba(234, 179, 8, 0.1);
    }
    .badge-low {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        color: #991b1b;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.82rem;
        border: 1px solid #fca5a5;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);
    }
    .badge-domain {
        background: #f1f5f9;
        color: #1e293b;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid #cbd5e1;
    }
    .badge-evidence {
        background: #e0f2fe;
        color: #0369a1;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid #bae6fd;
    }

    /* Keyword Highlight */
    mark.highlight {
        background: #fef08a;
        color: #713f12;
        padding: 2px 5px;
        border-radius: 4px;
        font-weight: 600;
    }

    /* Pipeline Banner */
    .pipeline-step-box {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        max-width: 980px;
        margin: 0 auto 24px auto;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 14px 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    .pipeline-node {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        width: 110px;
        flex-shrink: 0;
    }
    .pipeline-node-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        margin-bottom: 6px;
    }
    .pipeline-node-active .pipeline-node-icon {
        background: linear-gradient(135deg, #0284c7, #6366f1);
        color: white;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
    }
    .pipeline-node-text {
        font-size: 0.75rem;
        font-weight: 600;
        color: #475569;
    }
    .pipeline-arrow {
        color: #94a3b8;
        font-size: 1.1rem;
        padding: 0 2px;
        flex-shrink: 0;
        opacity: 0.7;
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
    st.caption("Autonomous Research Platform • Version 2.0")
    st.markdown("---")

    st.markdown("#### ⚙️ Orchestration Controls")
    max_results = st.slider(
        "Max Search Results",
        min_value=3,
        max_value=8,
        value=5,
        help="Number of web sources to query, validate, and scrape.",
    )

    domain_filter = st.text_input(
        "Domain Filter (Optional)",
        placeholder="e.g. org, edu, wikipedia.org",
        help="Target a specific domain or TLD.",
    )

    st.markdown("---")
    st.markdown("#### 💡 Quick Benchmark Presets")
    st.caption("Click to load verified test queries:")

    test_queries = [
        ("🌱 Renewable Energy", "What are the benefits of renewable energy?"),
        ("🌿 Photosynthesis (403 Test)", "How does photosynthesis work?"),
        ("⚛️ Quantum Computing", "What are the latest developments in quantum computing?"),
        ("❌ Negative Query Test", "xyzabcqwerty9876543210nonexistentquery"),
    ]

    for label, q_text in test_queries:
        if st.button(label, key=f"btn_{label}", use_container_width=True):
            st.session_state["active_query"] = q_text

    st.markdown("---")
    st.markdown("#### 🛡️ Production Safeguards")
    st.markdown(
        """
        <div style="font-size: 0.85rem; line-height: 1.8; color: #475569;">
            <div>🔒 <strong>SSRF Protection</strong>: RFC 1918 & Localhost blocked</div>
            <div>📑 <strong>Type Filter</strong>: Strict HTML Content-Type only</div>
            <div>⏱️ <strong>Timeout Caps</strong>: 10s fetch / 25s search timeout</div>
            <div>🌐 <strong>Source Grounding</strong>: 100% genuine URL citations</div>
            <div>🧪 <strong>Offline Tests</strong>: 23/23 passing via pytest</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("Built with Python • DuckDuckGo • BeautifulSoup4 • Plotly")

# -----------------------------------------------------------------------------
# Hero Section
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">🔬 AI Research Agent</div>
        <div class="hero-subtitle">
            Autonomous information retrieval and visual evidence synthesis platform with deterministic 13-step orchestration, dual tool delegation, and enterprise-grade SSRF security.
        </div>
        <div class="hero-tags">
            <span class="badge-pill"><span class="pulse-dot"></span> Agent Engine Live</span>
            <span class="badge-pill">🔍 DuckDuckGo (ddgs)</span>
            <span class="badge-pill">🌐 BeautifulSoup4 Scraper</span>
            <span class="badge-pill">🛡️ SSRF Guarded</span>
            <span class="badge-pill">📊 Plotly Analytics</span>
            <span class="badge-pill">🧪 23 Unit Tests</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Visual Pipeline Stepper
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="pipeline-step-box">
        <div class="pipeline-node pipeline-node-active">
            <div class="pipeline-node-icon">📋</div>
            <div class="pipeline-node-text">1. Ingest & Validate</div>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node pipeline-node-active">
            <div class="pipeline-node-icon">🗺️</div>
            <div class="pipeline-node-text">2. Formulate Plan</div>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node pipeline-node-active">
            <div class="pipeline-node-icon">🔍</div>
            <div class="pipeline-node-text">3. Web Search</div>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node pipeline-node-active">
            <div class="pipeline-node-icon">🛡️</div>
            <div class="pipeline-node-text">4. SSRF & Scrape</div>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node pipeline-node-active">
            <div class="pipeline-node-icon">📊</div>
            <div class="pipeline-node-text">5. Rank & Score</div>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-node pipeline-node-active">
            <div class="pipeline-node-icon">📑</div>
            <div class="pipeline-node-text">6. Structured Report</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Query Input & Action Bar
# -----------------------------------------------------------------------------
initial_query = st.session_state.get("active_query", "")

query_input = st.text_input(
    "Research Question:",
    value=initial_query,
    placeholder="Ask any research question...",
)

col_run, col_clear, _ = st.columns([1.5, 1.2, 5])
with col_run:
    run_btn = st.button("🚀 Run Research", type="primary", use_container_width=True)

with col_clear:
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state["history"] = []
        st.session_state["current_report"] = None
        st.session_state["active_query"] = ""
        st.rerun()

# -----------------------------------------------------------------------------
# Live Orchestration Execution
# -----------------------------------------------------------------------------
if run_btn:
    if not query_input.strip():
        st.error("⚠️ Please provide a non-empty research question.")
    else:
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

        st.session_state["current_report"] = report
        st.session_state["history"].append({
            "timestamp": time.strftime("%H:%M:%S"),
            "query": query_input.strip(),
            "report": report,
        })

# -----------------------------------------------------------------------------
# Research Session History Selector
# -----------------------------------------------------------------------------
if st.session_state["history"]:
    st.markdown("#### 📂 Session History")
    hist_cols = st.columns(min(len(st.session_state["history"]), 4))
    for idx, item in enumerate(reversed(st.session_state["history"][-4:])):
        with hist_cols[idx]:
            label = f"🕒 {item['timestamp']}: {item['query'][:20]}..."
            if st.button(label, key=f"hist_{idx}", use_container_width=True):
                st.session_state["current_report"] = item["report"]
                st.rerun()

# -----------------------------------------------------------------------------
# Report Presentation & Visual Analytics
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
            label="⚡ Execution Latency",
            value=f"{rep['execution_time_seconds']}s",
            help="Total time for search, SSRF checks, scraping, and scoring.",
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
            <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 18px 22px; border-radius: 16px; box-shadow: 0 4px 12px -2px rgba(0,0,0,0.04);">
                <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;">🛡️ Confidence Level</div>
                <div style="margin-top: 8px; display: flex; align-items: center; gap: 8px;">
                    <span class="{badge_cls}">{conf_level.upper()}</span>
                    <span style="font-size: 0.9rem; font-weight: 700; color: #475569;">({conf.get('score', 0)}/5 pts)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.metric(
            label="🌐 Scrape Ratio",
            value=f"{rep['sources_extracted']} / {rep['sources_validated']}",
            help="Webpages successfully scraped vs validated safe URLs.",
        )
    with m4:
        avg_rel = (
            sum(f["relevance_score"] for f in findings) / len(findings)
            if findings else 0.0
        )
        st.metric(
            label="🎯 Avg Relevance",
            value=f"{avg_rel:.0%}",
            help="Average keyword match density across all retrieved evidence.",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Executive Short Answer Card
    st.markdown(
        f"""
        <div class="summary-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.3rem;">💡</span>
                    <h3 style="margin: 0; color: #0369a1; font-size: 1.25rem; font-weight: 700;">Executive Synthesis</h3>
                </div>
                <span class="{badge_cls}">Confidence: {conf_level}</span>
            </div>
            <p style="font-size: 1.1rem; line-height: 1.65; color: #0f172a; margin-bottom: 16px; font-weight: 500;">
                {rep['short_answer']}
            </p>
            <div style="font-size: 0.85rem; color: #475569; background: rgba(255, 255, 255, 0.7); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(226, 232, 240, 0.8);">
                <strong>Heuristic Rationale:</strong> {conf['explanation']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Interactive Visual Analytics Section
    st.markdown("### 📊 Interactive Visual Analytics")

    vcol1, vcol2 = st.columns([3, 2])

    with vcol1:
        st.markdown("##### Source Relevance & Evidence Quality")
        if findings:
            chart_data = []
            for f in findings:
                domain = get_domain(f["source_url"])
                title_short = (f["source_title"][:26] + "..") if len(f["source_title"]) > 26 else f["source_title"]
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
            fig_bar.update_traces(
                texttemplate="%{text:.0f}%",
                textposition="outside",
                marker=dict(line=dict(width=1, color="rgba(255,255,255,0.4)")),
            )
            fig_bar.update_layout(
                yaxis={"autorange": "reversed"},
                margin={"l": 20, "r": 30, "t": 10, "b": 20},
                height=280,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans", size=12),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No sources met the relevance threshold for charting.")

    with vcol2:
        st.markdown("##### Confidence Score Breakdown (0–5 pts)")
        total_score = conf.get("score", 0)

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=total_score,
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 5], "tickwidth": 1, "tickcolor": "#64748b"},
                    "bar": {"color": "#0284c7", "thickness": 0.28},
                    "bgcolor": "white",
                    "steps": [
                        {"range": [0, 2], "color": "#fee2e2"},
                        {"range": [2, 4], "color": "#fef9c3"},
                        {"range": [4, 5], "color": "#dcfce7"},
                    ],
                    "threshold": {
                        "line": {"color": "#10b981", "width": 4},
                        "thickness": 0.8,
                        "value": 4.0,
                    },
                },
            )
        )
        fig_gauge.update_layout(
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
            height=200,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        c_ext = conf.get("extracted_score", 0)
        c_rel = conf.get("relevance_score", 0)
        c_div = conf.get("diversity_score", 0)
        st.caption(
            f"**Heuristic Points:** Extracted Pages: **+{c_ext}** | "
            f"Keyword Density: **+{c_rel}** | "
            f"Domain Variety: **+{c_div}**"
        )

    # 4. Pipeline Funnel & Content Depth Row
    fcol1, fcol2 = st.columns([1, 1])

    with fcol1:
        st.markdown("##### Retrieval Funnel Progression")
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
            height=210,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans"),
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    with fcol2:
        st.markdown("##### Extracted Content Depth (Word Count)")
        if findings:
            lengths_data = []
            for f in findings:
                domain = get_domain(f["source_url"])
                word_count = len(f["text"].split())
                lengths_data.append({
                    "Source": domain,
                    "Word Count": word_count,
                    "Evidence Type": f["evidence_type"],
                })
            df_len = pd.DataFrame(lengths_data)
            fig_len = px.bar(
                df_len,
                x="Source",
                y="Word Count",
                color="Evidence Type",
                color_discrete_map={
                    "Extracted webpage content": "#0284c7",
                    "Search snippet": "#f59e0b",
                },
                text="Word Count",
            )
            fig_len.update_traces(textposition="outside")
            fig_len.update_layout(
                margin={"l": 20, "r": 20, "t": 10, "b": 10},
                height=210,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Plus Jakarta Sans"),
            )
            st.plotly_chart(fig_len, use_container_width=True)
        else:
            st.info("No content available for word count analysis.")

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
            "📦 Report Export Center",
        ]
    )

    # TAB 1: Key Findings with Keyword Highlighting
    with tab_findings:
        if not findings:
            st.warning("No findings passed the relevance threshold. Try rephrasing your research query.")
        else:
            for i, f in enumerate(findings, 1):
                domain = get_domain(f["source_url"])
                highlighted_excerpt = highlight_keywords(f["text"][:450], rep["question"])
                rel_pct = f"{f['relevance_score']:.0%}"

                st.markdown(
                    f"""
                    <div class="finding-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="background: #0284c7; color: white; border-radius: 50%; width: 26px; height: 26px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: 700;">#{i}</span>
                                <h4 style="margin: 0; font-size: 1.15rem; font-weight: 700;">
                                    <a href="{f['source_url']}" target="_blank" style="text-decoration: none; color: #0284c7;">{f['source_title']}</a>
                                </h4>
                            </div>
                            <div style="display: flex; gap: 6px;">
                                <span class="badge-domain">🌐 {domain}</span>
                                <span class="badge-evidence">{f['evidence_type']}</span>
                            </div>
                        </div>
                        <div style="margin: 8px 0 12px 0;">
                            <span style="font-size: 0.85rem; font-weight: 600; color: #475569;">
                                🎯 Keyword Match Density: <strong style="color: #0284c7;">{rel_pct}</strong>
                            </span>
                        </div>
                        <div style="background: #f8fafc; border-left: 4px solid #0284c7; padding: 14px 16px; border-radius: 8px; font-size: 0.98rem; line-height: 1.65; color: #334155; margin-bottom: 10px;">
                            "{highlighted_excerpt}{'...' if len(f['text']) > 450 else ''}"
                        </div>
                        <div style="font-size: 0.82rem; color: #64748b;">
                            Source URL: <a href="{f['source_url']}" target="_blank" style="color: #64748b; word-break: break-all;">{f['source_url']}</a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander(f"📄 View Full Raw Text for Finding #{i}"):
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
        st.caption("Deterministic trace generated step-by-step during this query execution:")
        st.code("\n".join(rep["execution_log"]), language="text")

    # TAB 4: In-App Documentation Explorer
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

        json_export = json.dumps(rep, indent=2, ensure_ascii=False)

        md_export = f"""# Research Report: {rep['question']}

**Execution Time:** {rep['execution_time_seconds']}s  
**Confidence Level:** {conf['level']}  
**Confidence Rationale:** {conf['explanation']}  

---

## Executive Synthesis
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
        <h3>Executive Synthesis</h3>
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
