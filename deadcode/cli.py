"""Command-line interface for DeadCode."""
from __future__ import annotations

import argparse
import json
import sys

from .analyzer import analyze_file
from .history import get_history
from .ollama_client import DEFAULT_MODEL, OllamaError, explain_with_ollama


BANNER = r"""
 ____            _  ____          _
|  _ \  ___  __| |/ ___|___   __| | ___
| | | |/ _ \/ _` | |   / _ \ / _` |/ _ \
| |_| |  __/ (_| | |__| (_) | (_| |  __/
|____/ \___|\__,_|\____\___/ \__,_|\___|

       THE SPIRIT OF FORGOTTEN LANGUAGES
"""


def _print_analysis(result, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), indent=2))
        return
    print(BANNER)
    print("DeadCode | Static Analysis")
    print(f"File: {result.filename}")
    print(f"Language: {result.language}")
    print(f"Lines: {result.line_count}\n")
    print(result.summary)
    print()
    for finding in result.findings:
        location = f" (line {finding.line})" if finding.line else ""
        print(f"[{finding.severity}] {finding.title}{location}")
        print(f"       {finding.detail}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deadcode",
        description="A local-first AI companion for understanding legacy code.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Run heuristic static checks on a source file.")
    analyze.add_argument("file", help="Path to a COBOL, BASIC, or text source file.")
    analyze.add_argument("--json", action="store_true", help="Print machine-readable JSON.")

    explain = sub.add_parser("explain", help="Explain a legacy source file.")
    explain.add_argument("file", help="Path to the source file.")
    explain.add_argument("--ai", action="store_true", help="Use a local Ollama model.")
    explain.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model name (default: {DEFAULT_MODEL}).")

    history = sub.add_parser("history", help="Explore a language's background.")
    history.add_argument("language", choices=["cobol", "basic"], help="Language to explore.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            _print_analysis(analyze_file(args.file), args.json)
        elif args.command == "explain":
            result = analyze_file(args.file)
            _print_analysis(result)
            if args.ai:
                source = open(args.file, "r", encoding="utf-8", errors="replace").read()
                print("\n" + "=" * 68 + "\nLOCAL AI EXPLANATION\n" + "=" * 68 + "\n")
                print(explain_with_ollama(source, result.language, args.model))
            else:
                print("\nTip: add --ai to request an explanation from a local Ollama model.")
        elif args.command == "history":
            note = get_history(args.language)
            print(BANNER)
            print(f"{note['name']} | A short history")
            print(f"Era: {note['era']}\n")
            print(note["context"])
            print(f"\nPreservation question: {note['question']}")
    except (OSError, ValueError, OllamaError) as exc:
        print(f"deadcode: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
