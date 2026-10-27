# DeadCode: The Spirit of Forgotten Languages 👻

> Give legacy code a second life.

DeadCode is an open-source AI coding companion for exploring, understanding, and preserving older programming languages such as **COBOL** and **BASIC**. It combines deterministic, local analysis with an optional open-weight language model running through [Ollama](https://ollama.com/).

It is designed for the **Ghost in the Machine** theme: the code may be old, but its logic still has stories to tell.

## What it does

- **Explain legacy code** in plain English.
- **Detect common warning patterns** with lightweight static checks.
- **Explore historical context** for COBOL and BASIC without pretending every program has the same history.
- **Run locally** with Ollama, so source code does not need to be sent to a hosted AI API.
- **Work without AI** using deterministic checks when Ollama is not installed or available.

### Current language support

- **COBOL:** recognizes common divisions, sections, and statements; includes starter warning patterns.
- **BASIC:** recognizes common classic BASIC statements and line-numbered programs; includes starter warning patterns.
- **Unknown / mixed:** still accepts source text and offers general analysis.

This is an educational MVP, not a full compiler, formal verifier, or replacement for a language-specific linter.

## Quick start

Requires Python 3.10 or newer. No third-party Python packages are needed.

```bash
git clone https://github.com/YOUR-USERNAME/deadcode.git
cd deadcode
python -m deadcode.cli analyze examples/haunted_payroll.cob
```

Explain a file:

```bash
python -m deadcode.cli explain examples/haunted_payroll.cob
```

Explore language history:

```bash
python -m deadcode.cli history cobol
python -m deadcode.cli history basic
```

### Optional: enable a local open-weight model

1. Install Ollama from https://ollama.com/
2. Pull a model that fits your hardware. For example:

```bash
ollama pull qwen2.5-coder:3b
```

3. Keep Ollama running, then:

```bash
python -m deadcode.cli explain examples/haunted_payroll.cob --ai
```

DeadCode calls Ollama's local HTTP API at `http://localhost:11434`. Set a different endpoint with `OLLAMA_HOST` or choose a model with `--model`.

```bash
OLLAMA_HOST=http://127.0.0.1:11434 python -m deadcode.cli explain examples/old_basic.bas --ai --model qwen2.5-coder:3b
```

The model is optional. `analyze` and `history` work without it. Once the model has been downloaded, local inference can run without an internet connection, depending on your Ollama setup.

## Example output

```text
$ python -m deadcode.cli analyze examples/haunted_payroll.cob

DeadCode | Static Analysis
File: examples/haunted_payroll.cob
Language: COBOL
Lines: 22

[INFO] Structure: IDENTIFICATION DIVISION found.
[INFO] Structure: PROCEDURE DIVISION found.
[WARN] Review: DISPLAY statement found. Check whether output may expose sensitive data.
[INFO] Preservation note: This is a small teaching example, not production payroll software.
```

Exact findings depend on the source file and the checks implemented in this version.

## Why open innovation matters

Legacy code can contain business rules that are difficult to reconstruct. Sending proprietary source code to an external service may be unacceptable for teams maintaining old systems. DeadCode's local-first design lets developers inspect source with deterministic checks and optionally ask an open-weight model for explanations on their own machine.

Open models also make the model layer replaceable. Developers can change models, inspect the prompts, and adapt the tool without depending on a single hosted AI API. The project remains useful when AI is unavailable because its basic analysis is ordinary Python code.

**Privacy note:** local inference avoids sending code to a hosted model through DeadCode, but your environment, telemetry settings, or other software may still make network requests. Verify your own setup for sensitive code.

## Project layout

```text
deadcode/
├── deadcode/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── cli.py
│   ├── history.py
│   └── ollama_client.py
├── examples/
│   ├── haunted_payroll.cob
│   └── old_basic.bas
├── tests/
│   └── test_analyzer.py
├── .gitignore
├── LICENSE
└── README.md
```

## Development and tests

```bash
python -m unittest discover -s tests -v
```

No dependencies are required for the static analyzer or tests.

## Safety and limitations

- DeadCode **does not execute** source code or shell commands.
- Findings are heuristics, not proof of a defect or vulnerability.
- The AI may hallucinate details. Verify explanations against the source and authoritative documentation.
- Historical notes are high-level orientation, not a substitute for archival research.
- Never upload confidential source code to a model or service unless you have permission.

## Contributing

Issues and pull requests are welcome. Useful contributions include more COBOL/BASIC patterns, additional legacy languages, carefully sourced history notes, test fixtures, and improvements to local-model compatibility.

Please include tests for new analyzer rules and cite sources when adding historical claims.

## License

MIT. See [LICENSE](LICENSE).
