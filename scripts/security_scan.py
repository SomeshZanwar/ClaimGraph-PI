from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "mlruns",
    "artifacts",
    "__pycache__",
    "target",
}
TEXT_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".mjs",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".md",
    ".html",
    ".css",
    ".env",
    ".txt",
    ".conf",
}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "OpenAI-style API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub personal access token": re.compile(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
}


def scan() -> list[str]:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".env.example":
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(content):
                line_number = content.count("\n", 0, match.start()) + 1
                findings.append(
                    f"{path.relative_to(ROOT)}:{line_number}: possible {label}"
                )
    return findings


def main() -> None:
    findings = scan()
    if findings:
        print("Potential committed secrets found:")
        for finding in findings:
            print(f"  {finding}")
        raise SystemExit(1)

    print("Secret pattern scan passed.")


if __name__ == "__main__":
    main()
