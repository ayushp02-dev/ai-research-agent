"""
AI Research Agent — Command-line entry point.

Usage:
    python main.py "What are the benefits of renewable energy?"
    python main.py --max-results 3 "How does photosynthesis work?"
    python main.py --json "What is machine learning?"
    python main.py                          # interactive prompt
"""

import argparse
import json
import logging
import sys

from research_agent import ResearchAgent


def format_report(report):
    """
    Format a research report dict into a human-readable terminal display.

    Args:
        report: The structured report dict returned by ResearchAgent.research().

    Returns:
        A formatted string suitable for printing to the terminal.
    """
    lines = []
    sep = "=" * 60

    lines.append(sep)
    lines.append("  RESEARCH REPORT")
    lines.append(sep)

    lines.append(f"\nQUESTION: {report['question']}\n")

    lines.append("SHORT ANSWER:")
    lines.append(f"  {report['short_answer']}\n")

    conf = report["confidence"]
    lines.append(f"CONFIDENCE: {conf['level']}")
    lines.append(f"  {conf['explanation']}\n")

    findings = report["findings"]
    lines.append(f"KEY FINDINGS ({len(findings)} source(s)):")
    lines.append("-" * 60)

    for i, finding in enumerate(findings, 1):
        lines.append(f"\n  Finding {i}:")
        lines.append(f"    Title:      {finding['source_title']}")
        lines.append(f"    URL:        {finding['source_url']}")
        lines.append(f"    Type:       {finding['evidence_type']}")
        lines.append(f"    Relevance:  {finding['relevance_score']:.0%}")
        preview = finding["text"][:200]
        if len(finding["text"]) > 200:
            preview += "..."
        lines.append(f"    Preview:    {preview}")

    if not findings:
        lines.append("  (No findings available)")

    lines.append(f"\nLIMITATIONS:")
    for lim in report["limitations"]:
        lines.append(f"  - {lim}")

    lines.append(f"\nSUGGESTED NEXT STEPS:")
    for step in report["next_steps"]:
        lines.append(f"  - {step}")

    lines.append(f"\nExecution time: {report['execution_time_seconds']}s")
    lines.append(
        f"Sources: {report['sources_searched']} searched -> "
        f"{report['sources_validated']} validated -> "
        f"{report['sources_extracted']} extracted"
    )
    lines.append(sep)

    return "\n".join(lines)


def setup_logging(verbose=False):
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    """Parse arguments and run the research agent."""
    parser = argparse.ArgumentParser(
        description=(
            "AI Research Agent — A rule-based research tool that searches "
            "the web and generates structured reports with source attribution."
        ),
        epilog='Example: python main.py "What are the benefits of renewable energy?"',
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="The research question to investigate",
    )
    parser.add_argument(
        "--max-results", "-n",
        type=int,
        default=5,
        help="Maximum number of search results to process (default: 5)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON report instead of formatted text",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    # Interactive prompt if no question provided
    question = args.question
    if not question:
        print("\n--- AI Research Agent ---")
        print("=" * 40)
        try:
            question = input("Enter your research question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            sys.exit(0)

    if not question:
        print("Error: No research question provided.")
        sys.exit(1)

    # Run the research workflow
    agent = ResearchAgent(max_search_results=args.max_results)
    report = agent.research(question)

    # Display the report
    if args.json:
        output_str = json.dumps(report, indent=2, ensure_ascii=True)
    else:
        output_str = format_report(report)

    try:
        print(output_str)
    except UnicodeEncodeError:
        print(output_str.encode("ascii", errors="replace").decode("ascii"))

    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    main()
