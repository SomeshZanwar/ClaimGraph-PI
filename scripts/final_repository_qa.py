from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = ROOT / "frontend" / "src"
FRONTEND_PUBLIC = ROOT / "frontend" / "public"

REQUIRED_PATHS = [
    ROOT / "README.md",
    ROOT / "SECURITY.md",
    ROOT / "PRD.md",
    ROOT / "Architecture.md",
    ROOT / "rules.md",
    ROOT / "phases.md",
    ROOT / "design.md",
    ROOT / "memory.md",
    ROOT / "frontend" / "package-lock.json",
    FRONTEND_PUBLIC / "favicon.svg",
    FRONTEND_PUBLIC / "llms.txt",
    FRONTEND_PUBLIC / "social-preview.svg",
]

FORBIDDEN_SOURCE_SNIPPETS = {
    "placeholder UI text": "placeholder=",
    "empty anchor": 'href="#"',
    "em dash in shipped UI copy": "—",
    "Inter font": "font-family: Inter",
    "Geist font": "font-family: Geist",
    "Space Grotesk font": "font-family: Space Grotesk",
    "unfinished TODO": "TODO",
    "unfinished FIXME": "FIXME",
}


def iter_frontend_text_files() -> list[Path]:
    allowed = {".ts", ".tsx", ".css", ".html", ".txt", ".svg", ".mjs"}
    files: list[Path] = []
    for base in (FRONTEND_SRC, FRONTEND_PUBLIC, ROOT / "frontend"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if "node_modules" in path.parts or "dist" in path.parts:
                continue
            if path.suffix.lower() in allowed:
                files.append(path)
    return sorted(set(files))


def main() -> None:
    failures: list[str] = []

    for path in REQUIRED_PATHS:
        if not path.exists():
            failures.append(f"Missing required repository file: {path.relative_to(ROOT)}")

    for path in iter_frontend_text_files():
        text = path.read_text(encoding="utf-8")
        for label, snippet in FORBIDDEN_SOURCE_SNIPPETS.items():
            if snippet in text:
                failures.append(
                    f"{path.relative_to(ROOT)} contains prohibited {label}: {snippet!r}"
                )

    app_source = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
    for required_copy in (
        "Privacy Policy",
        "Terms of Service",
        "Support and bug reports",
        "Page not found",
        "Investigation support only",
    ):
        if required_copy not in app_source:
            failures.append(f"Missing required public UI content: {required_copy}")

    index_html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    if 'name="description"' not in index_html:
        failures.append("frontend/index.html has no meta description")
    if 'rel="icon"' not in index_html:
        failures.append("frontend/index.html has no favicon")
    if "noindex" in index_html.lower():
        failures.append("frontend/index.html contains an unintended noindex directive")

    if failures:
        print("Final repository QA failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(
        "Final repository QA passed: required files, shipped UI hygiene, "
        "legal/support content, metadata, and repository lockfile are present."
    )


if __name__ == "__main__":
    main()
