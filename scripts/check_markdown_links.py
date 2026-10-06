from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"!?[[^]]*](([^)]+))")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#")


def iter_markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
        and "node_modules" not in path.parts
        and ".venv" not in path.parts
    )


def resolve_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().split()[0].strip("<>")
    if not target or target.startswith(SKIP_PREFIXES):
        return None

    target = unquote(target.split("#", 1)[0])
    if not target:
        return None

    if target.startswith("/"):
        return None

    return (source.parent / target).resolve()


def main() -> None:
    failures: list[str] = []

    for source in iter_markdown_files():
        text = source.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = resolve_target(source, match.group(1))
            if target is None:
                continue

            try:
                target.relative_to(ROOT)
            except ValueError:
                failures.append(
                    f"{source.relative_to(ROOT)} -> path escapes repository: {target}"
                )
                continue

            if not target.exists():
                failures.append(
                    f"{source.relative_to(ROOT)} -> missing target: "
                    f"{target.relative_to(ROOT)}"
                )

    if failures:
        print("Broken local Markdown links found:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("Local Markdown links are valid.")


if __name__ == "__main__":
    main()
