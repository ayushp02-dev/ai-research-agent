"""
AI Research Agent — Streamlit Interactive Web Application.

A modern, interview-ready interface for demonstrating the autonomous,
rule-based research agent pipeline with live orchestration progress,
evidence ranking, confidence heuristics, and exportable reports.
"""

import json
import time
import streamlit as st

from research_agent import ResearchAgent

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Agent | Predixion",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Custom Styling (Clean Modern Dashboard)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 14px 18px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 600;
        color: #475569;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
    }
    /* Summary Card */
    .summary-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    /* Finding Card */
    .finding-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .finding-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    /* Badges */
    .badge-high {
        background-color: #dcfce7;
        color: #15803d;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-moderate {
        background-color: #fef9c3;
        color: #a16207;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-low {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-source {
        background-color: #ede9fe;
        color: #6d28d9;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Sidebar Configuration & Architecture Overview
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔬 System Architecture")
    st.markdown(
        """
        **Predixion Platform Engineer**  
        *Autonomous Rule-Based Agent*
        """
    )
    st.markdown("---")

    st.markdown("#### ⚙️ Research Parameters")
    max_results = st.slider(
        "Max Search Results",
        min_value=3,
        max_value=10,
        value=5,
        help="Number of web sources to retrieve and analyze.",
    )

    st.markdown("---")
    st.markdown("#### 💡 Quick Test Queries")
    st.caption("Click any query to load into the research input:")

    sample_questions = [
        "What are the benefits of renewable energy?",
        "How does photosynthesis work?",
        "What are the latest developments in quantum computing?",
        "xyzabcqwerty9876543210nonexistentquery",
    ]

    for q in sample_questions:
        if st.button(f"🔍 {q[:32]}...", key=f"btn_{q}"):
            st.session_state["query_input"] = q

    st.markdown("---")
    st.markdown("#### 🛡️ Active Safeguards")
    st.markdown(
        """
        - ✅ **SSRF Protection** (Blocks private IPs & localhost)
        - ✅ **Content-Type Filter** (HTML only, no binary)
        - ✅ **Timeout Protection** (10s fetch / 25s search)
        - ✅ **Zero Hallucination** (100% genuine URL citations)
        - ✅ **Offline Test Suite** (23 / 23 `pytest` passing)
        """
    )

    st.markdown("---")
    st.caption("No paid APIs or OpenAI keys used. Deterministic orchestration.")

# -----------------------------------------------------------------------------
# Main Header
# -----------------------------------------------------------------------------
st.title("🔬 AI Research Agent")
st.markdown(
    "**Autonomous Rule-Based Information Retrieval & Synthesis Platform** • "
    "*Predixion Platform Engineer Internship Project*"
)

st.markdown(
    """
    <div style="display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap;">
        <span class="badge-source">DuckDuckGo Search</span>
        <span class="badge-source">BeautifulSoup4 Scraper</span>
        <span class="badge-source">SSRF Protected</span>
        <span class="badge-source">13-Step Orchestration</span>
        <span class="badge-source">Zero Paid APIs</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Query Input Box
# -----------------------------------------------------------------------------
default_query = st.session_state.get(
    "query_input", "What are the benefits of renewable energy?"
)

query = st.text_input(
    "Enter Research Question:",
    value=default_query,
    placeholder="e.g., How does photosynthesis work? or What is quantum computing?",
)

col_run, col_clear = st.columns([1, 5])
with col_run:
    start_btn = st.button("🚀 Start Research", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# Agent Execution & Live Progress
# -----------------------------------------------------------------------------
if start_btn:
    if not query.strip():
        st.warning("⚠️ Please enter a valid, non-empty research question.")
    else:
        # Live status container
        status_box = st.status("🤖 Orchestrating Research Pipeline...", expanded=True)
        step_placeholders = {}

        def update_ui_step(step_num, message):
            step_icons = {
                1: "📋",
                2: "🗺️",
                3: "🛠️",
                4: "🔍",
                5: "🛡️",
                6: "🌐",
                7: "📊",
                8: "🔗",
                9: "📑",
                10: "⚖️",
                11: "⚠️",
                12: "⏱️",
                13: "✅",
            }
            icon = step_icons.get(step_num, "🔹")
            status_box.write(f"{icon} **Step {step_num}**: {message}")

        agent = ResearchAgent(
            max_search_results=max_results,
            verbose=False,
            step_callback=update_ui_step,
        )

        with st.spinner("Analyzing web sources and extracting findings..."):
            report = agent.research(query)

        status_box.update(
            label=f"✅ Research Complete in {report['execution_time_seconds']}s!",
            state="complete",
            expanded=False,
        )

        # Store in session state for tab navigation
        st.session_state["latest_report"] = report

# -----------------------------------------------------------------------------
# Report Presentation
# -----------------------------------------------------------------------------
if "latest_report" in st.session_state:
    rep = st.session_state["latest_report"]
    conf = rep["confidence"]
    findings = rep["findings"]

    st.markdown("---")
    st.subheader("📑 Research Report")

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Execution Latency", value=f"{rep['execution_time_seconds']}s")
    with m2:
        conf_level = conf["level"]
        badge_class = (
            "badge-high"
            if conf_level == "High"
            else "badge-moderate" if conf_level == "Moderate" else "badge-low"
        )
        st.markdown(
            f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px 18px; border-radius: 12px;">
                <div style="font-size: 0.85rem; font-weight: 600; color: #475569;">Confidence Level</div>
                <div style="margin-top: 6px;"><span class="{badge_class}">{conf_level.upper()}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.metric(
            label="Sources Extracted",
            value=f"{rep['sources_extracted']} / {rep['sources_validated']}",
        )
    with m4:
        avg_rel = (
            f"{sum(f['relevance_score'] for f in findings) / len(findings):.0%}"
            if findings
            else "0%"
        )
        st.metric(label="Avg Keyword Relevance", value=avg_rel)

    st.markdown("<br>", unsafe_allow_html=True)

    # Executive Summary Card
    st.markdown(
        f"""
        <div class="summary-card">
            <h4 style="margin-top: 0; color: #0369a1;">Executive Short Answer</h4>
            <p style="font-size: 1.05rem; line-height: 1.6; color: #0f172a; margin-bottom: 8px;">
                {rep['short_answer']}
            </p>
            <small style="color: #64748b;">
                <strong>Confidence Rationale:</strong> {conf['explanation']}
            </small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tabs for Structured Data
    tab_findings, tab_transparency, tab_log, tab_raw = st.tabs(
        [
            f"🔍 Key Findings ({len(findings)})",
            "⚖️ Limitations & Next Steps",
            "📜 13-Step Execution Log",
            "📦 Raw JSON Report",
        ]
    )

    # TAB 1: Key Findings
    with tab_findings:
        if not findings:
            st.info(
                "No findings passed the relevance threshold. Try rephrasing your research question."
            )
        else:
            for i, f in enumerate(findings, 1):
                with st.container():
                    st.markdown(
                        f"""
                        <div class="finding-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <h4 style="margin: 0; font-size: 1.05rem;">
                                    Finding {i}: <a href="{f['source_url']}" target="_blank" style="text-decoration: none; color: #0284c7;">{f['source_title']}</a>
                                </h4>
                                <span class="badge-source">{f['evidence_type']}</span>
                            </div>
                            <div style="margin-bottom: 8px;">
                                <span style="font-size: 0.85rem; color: #475569;">
                                    <strong>Keyword Match Relevance:</strong> {f['relevance_score']:.0%}
                                </span>
                            </div>
                            <p style="color: #334155; font-size: 0.95rem; line-height: 1.5; background: #f8fafc; padding: 12px; border-radius: 8px; border-left: 3px solid #0284c7;">
                                "{f['text'][:350]}{'...' if len(f['text']) > 350 else ''}"
                            </p>
                            <small style="color: #64748b;">
                                Source: <code>{f['source_url']}</code>
                            </small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # TAB 2: Limitations & Next Steps
    with tab_transparency:
        col_lim, col_nxt = st.columns(2)
        with col_lim:
            st.markdown("#### ⚠️ Documented Limitations")
            for lim in rep["limitations"]:
                st.markdown(f"- {lim}")
        with col_nxt:
            st.markdown("#### 🧭 Suggested Next Steps")
            for step in rep["next_steps"]:
                st.markdown(f"- {step}")

    # TAB 3: Execution Log
    with tab_log:
        st.markdown("#### 📜 Verifiable Execution Audit Trail")
        st.caption(
            "Every step of the autonomous research process is deterministically recorded:"
        )
        log_text = "\n".join(rep["execution_log"])
        st.code(log_text, language="text")

    # TAB 4: Raw JSON & Export
    with tab_raw:
        st.markdown("#### 📦 Structured Machine-Readable Output")
        json_str = json.dumps(rep, indent=2, ensure_ascii=False)
        st.json(rep)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📥 Download JSON Report",
                data=json_str,
                file_name=f"research_report_{int(time.time())}.json",
                mime="application/json",
            )
        with col_d2:
            # Markdown export
            md_export = f"""# Research Report: {rep['question']}

**Execution Time:** {rep['execution_time_seconds']}s  
**Confidence:** {conf['level']} ({conf['explanation']})  

## Short Answer
{rep['short_answer']}

## Key Findings
"""
            for i, f in enumerate(findings, 1):
                md_export += f"""
### Finding {i}: [{f['source_title']}]({f['source_url']})
- **Type:** {f['evidence_type']}
- **Relevance:** {f['relevance_score']:.0%}
- **Excerpt:** {f['text'][:300]}...
"""
            st.download_button(
                label="📥 Download Markdown Report",
                data=md_export,
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
            )
