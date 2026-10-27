"""Short orientation notes for legacy language exploration.

These are intentionally high-level. Add sourced links in future contributions.
"""

NOTES = {
    "cobol": {
        "name": "COBOL",
        "era": "Designed in the late 1950s and standardized in the 1960s.",
        "context": (
            "COBOL was designed for business data processing. Its readable, "
            "division-based structure helped make record-oriented business logic "
            "explicit. It remains associated with long-lived transaction and "
            "batch systems, though actual deployments vary widely."
        ),
        "question": "Which business rule does this program encode, and what systems depend on it?",
    },
    "basic": {
        "name": "BASIC",
        "era": "Introduced in the 1960s as a beginner-friendly programming language.",
        "context": (
            "BASIC was created to make programming more accessible. Many early "
            "home-computer dialects used numbered lines and statements such as "
            "PRINT, INPUT, GOTO, and GOSUB. Syntax and capabilities vary by dialect."
        ),
        "question": "Which assumptions belong to the original machine or BASIC dialect?",
    },
}


def get_history(language: str) -> dict:
    key = language.strip().lower()
    aliases = {"cbl": "cobol", "cob": "cobol", "classic basic": "basic"}
    key = aliases.get(key, key)
    if key not in NOTES:
        raise ValueError(f"Unsupported language '{language}'. Choose: cobol, basic.")
    return NOTES[key]
