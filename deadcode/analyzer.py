"""Heuristic static analysis for small legacy-code examples.

This module intentionally does not parse or execute programs. Findings are
review prompts, not proof of bugs or vulnerabilities.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import re


@dataclass
class Finding:
    severity: str
    title: str
    detail: str
    line: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Analysis:
    filename: str
    language: str
    line_count: int
    summary: str
    findings: list[Finding]

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "language": self.language,
            "line_count": self.line_count,
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
        }


def detect_language(source: str, filename: str = "") -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".cob", ".cbl", ".cobol"}:
        return "COBOL"
    if suffix in {".bas", ".basic"}:
        return "BASIC"
    upper = source.upper()
    if "IDENTIFICATION DIVISION" in upper or "PROCEDURE DIVISION" in upper:
        return "COBOL"
    if re.search(r"(?im)^\s*\d+\s+(PRINT|LET|GOTO|GOSUB|INPUT)\b", source):
        return "BASIC"
    return "UNKNOWN"


def _line_findings(source: str, pattern: str, severity: str, title: str, detail: str):
    findings = []
    for number, line in enumerate(source.splitlines(), start=1):
        if re.search(pattern, line, flags=re.IGNORECASE):
            findings.append(Finding(severity, title, detail, number))
    return findings


def analyze_source(source: str, filename: str = "<memory>") -> Analysis:
    language = detect_language(source, filename)
    lines = source.splitlines()
    findings: list[Finding] = []

    if not source.strip():
        findings.append(Finding("WARN", "Empty source", "The file is empty or contains only whitespace."))
        return Analysis(filename, language, len(lines), "No source code was available to inspect.", findings)

    if language == "COBOL":
        upper = source.upper()
        if "IDENTIFICATION DIVISION" in upper:
            findings.append(Finding("INFO", "COBOL structure", "IDENTIFICATION DIVISION found."))
        else:
            findings.append(Finding("WARN", "Missing familiar structure", "No IDENTIFICATION DIVISION found. This may be a fragment rather than a complete program."))
        if "PROCEDURE DIVISION" in upper:
            findings.append(Finding("INFO", "COBOL structure", "PROCEDURE DIVISION found."))
        else:
            findings.append(Finding("WARN", "Missing procedure section", "No PROCEDURE DIVISION found. Confirm whether this is a partial snippet."))
        findings += _line_findings(source, r"\bACCEPT\b", "INFO", "Interactive input", "ACCEPT reads input. Check validation and assumptions about the input source.")
        findings += _line_findings(source, r"\bDISPLAY\b", "INFO", "Output statement", "DISPLAY writes output. Check whether the displayed value could contain sensitive data.")
        findings += _line_findings(source, r"\bGO\s+TO\b", "WARN", "Control-flow review", "GO TO can make control flow harder to follow. Review the surrounding logic before changing it.")
        findings += _line_findings(source, r"\bON\s+SIZE\s+ERROR\b", "INFO", "Arithmetic error handling", "An ON SIZE ERROR phrase appears. Verify that all relevant arithmetic paths handle overflow as intended.")
        findings += _line_findings(source, r"\bSTOP\s+RUN\b", "INFO", "Program termination", "STOP RUN terminates the run unit. Confirm this is appropriate for the program's calling context.")
        summary = "COBOL-oriented heuristic checks completed. These findings are prompts for review, not compiler diagnostics."
    elif language == "BASIC":
        findings += _line_findings(source, r"^\s*\d+\s+GOTO\b", "WARN", "Line-number jump", "Line-numbered GOTO can make flow difficult to maintain. Trace all jump targets before refactoring.")
        findings += _line_findings(source, r"\bINPUT\b", "INFO", "Interactive input", "INPUT accepts user-provided data. Validate assumptions about type and range.")
        findings += _line_findings(source, r"\bOPEN\b", "INFO", "File operation", "Review file mode, path assumptions, and error handling around this operation.")
        findings += _line_findings(source, r"\bON\s+ERROR\b", "INFO", "Error handling", "An error-handling statement appears. Check which failures it catches and whether errors can be silently ignored.")
        findings += _line_findings(source, r"\bPEEK\b|\bPOKE\b", "WARN", "Memory access", "PEEK/POKE are dialect- and platform-dependent memory operations. Verify the target environment before interpreting them.")
        if not findings:
            findings.append(Finding("INFO", "BASIC source detected", "No configured review patterns matched. This does not mean the program is bug-free."))
        summary = "Classic BASIC-oriented heuristic checks completed. Dialects differ, so interpret findings in context."
    else:
        findings.append(Finding("INFO", "General source review", "Language was not confidently detected. Provide a .cob/.cbl or .bas extension for language-specific checks."))
        findings += _line_findings(source, r"\b(TODO|FIXME|XXX)\b", "INFO", "Maintenance marker", "A TODO/FIXME-style marker may identify unfinished work.",)
        summary = "General text review completed. No language-specific parser was used."

    if len(lines) > 500:
        findings.append(Finding("INFO", "Large source file", f"This file has {len(lines)} lines. Consider analyzing smaller, logically related sections for clearer explanations."))

    return Analysis(filename, language, len(lines), summary, findings)


def analyze_file(path: str | Path) -> Analysis:
    file_path = Path(path)
    source = file_path.read_text(encoding="utf-8", errors="replace")
    return analyze_source(source, str(file_path))
