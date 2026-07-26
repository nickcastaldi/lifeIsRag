#!/usr/bin/env python3
"""
Prune a freshly-checked-out markdown tree down to genuine, English, security
content: drop non-English translations and repo/Jekyll boilerplate.

Usage: filter_markdown.py <directory>
Prints "<kept> <dropped>" to stdout on success.
"""
import re
import sys
from pathlib import Path

# Non-English language/locale directory names OWASP repos use for translation
# trees (e.g. CheatSheetSeries/, ASVS/4.0/<lang>/, .../translations/<lang>/).
# "en"/"en-us"/"en-gb" are deliberately absent so English content always stays.
LANG_DIRS = {
    "ar", "bg", "bn", "cs", "da", "de", "de-de", "el", "el-gr", "es", "es-es",
    "fa", "fi", "fr", "fr-fr", "he", "hi", "hr", "hu", "id", "it", "ja", "jp",
    "ka", "ko", "kr", "nl", "no", "pl", "pt", "pt-br", "pt-pt", "ro", "ru",
    "ru-ru", "sk", "sr", "sv", "ta", "te", "th", "tr", "uk", "vi", "zh",
    "zh-cn", "zh-hans", "zh-hant", "zh-tw",
}
LANG_FOLDER_NAMES = {"translations", "translation", "i18n", "locale", "locales", "localization", "l10n"}

# Matches a language code as a "-"/"_"/"." separated suffix of a path
# component, e.g. "2016-risks-zh-tw" or "m6-insecure-authorization-zh-tw.md"
# (compound codes like "zh-tw" listed first so they win over a bare "-tw").
_LANG_ALTERNATION = "|".join(re.escape(c) for c in sorted(LANG_DIRS, key=len, reverse=True))
LANG_SUFFIX_RE = re.compile(rf"[-_.](?:{_LANG_ALTERNATION})$", re.IGNORECASE)

# Filenames that are near-universally administrative/community boilerplate,
# not the repo's actual security content, validated against this corpus.
BOILERPLATE_NAMES = {
    "contributing.md", "code_of_conduct.md", "code-of-conduct.md",
    "changelog.md", "changes.md", "history.md",
    "pull_request_template.md", "issue_template.md", "bug_report.md",
    "feature_request.md", "security.md", "support.md", "funding.md",
    "license.md", "licence.md", "notice.md", "cla.md", "authors.md",
    "maintainers.md", "governance.md", "citation.md", "codeowners.md",
    # OWASP Jekyll sidebar metadata (project classification/leader blurbs)
    "leaders.md", "info.md",
    # Jekyll "tab" pages confirmed to be pure community/admin fluff, not
    # security content, by inspecting real examples across this corpus.
    # (tab_glossary/tab_related/tab_controls/tab_charter/tab_archive/etc.
    # were confirmed to hold genuine content and are deliberately NOT here.)
    "tab_acknowledgements.md", "tab_acknowledgments.md",
    "acknowledgements.md", "acknowledgments.md",
    "tab_sponsors.md", "sponsors.md",
    "tab_join.md", "join.md",
    "tab_example.md", "example.md",
    "tab_contributing.md", "tab_contributors.md", "contributors.md",
    "tab_download.md",
}
BOILERPLATE_PATH_SEGMENTS = {".github", "issue_template", "pull_request_template"}

# Lines that are just shields.io/badge/image markup, not prose.
BADGE_LINE_RE = re.compile(r"^\s*(\[!\[.*?\]\(.*?\)\]\(.*?\)|!\[.*?\]\(.*?\))\s*$")
LICENSE_BOILERPLATE_RE = re.compile(
    r"(creative commons attribution|licensed under a|cc-by-sa|licensebuttons\.net)",
    re.IGNORECASE,
)
MD_SYNTAX_RE = re.compile(r"[#*`_>\-\[\]()!|]")
README_MIN_WORDS = 10


def path_parts_lower(rel_path: Path):
    return [p.lower() for p in rel_path.parts]


def is_lang_component(component: str) -> bool:
    if component in LANG_FOLDER_NAMES or component in LANG_DIRS:
        return True
    return bool(LANG_SUFFIX_RE.search(component))


def is_translation(rel_path: Path) -> bool:
    parts = path_parts_lower(rel_path)
    dirs = parts[:-1]
    stem = rel_path.stem.lower()
    return any(is_lang_component(d) for d in dirs) or is_lang_component(stem)


def is_boilerplate_path(rel_path: Path) -> bool:
    name = rel_path.name.lower()
    parts = path_parts_lower(rel_path)
    dirs = parts[:-1]
    if name in BOILERPLATE_NAMES:
        return True
    if any(d in BOILERPLATE_PATH_SEGMENTS for d in dirs):
        return True
    # Placeholder READMEs living in image/asset folders ("# placeholder...")
    if name == "readme.md" and "images" in dirs:
        return True
    return False


def readme_has_substance(text: str) -> bool:
    kept_lines = []
    for line in text.splitlines():
        if BADGE_LINE_RE.match(line):
            continue
        if LICENSE_BOILERPLATE_RE.search(line):
            continue
        kept_lines.append(line)
    stripped = MD_SYNTAX_RE.sub(" ", "\n".join(kept_lines))
    words = [w for w in stripped.split() if any(c.isalpha() for c in w)]
    return len(words) >= README_MIN_WORDS


def should_drop(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if is_translation(rel):
        return True
    if is_boilerplate_path(rel):
        return True
    if rel.name.lower() == "readme.md":
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
        if not readme_has_substance(text):
            return True
    return False


def main():
    root = Path(sys.argv[1]).resolve()
    kept = 0
    dropped = 0
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() != ".md":
            continue
        if should_drop(path, root):
            path.unlink()
            dropped += 1
        else:
            kept += 1
    # Remove directories left empty by the pruning above (deepest first).
    for _ in range(6):
        empty_dirs = [d for d in sorted(root.rglob("*"), reverse=True) if d.is_dir() and not any(d.iterdir())]
        if not empty_dirs:
            break
        for d in empty_dirs:
            d.rmdir()
    print(f"{kept} {dropped}")


if __name__ == "__main__":
    main()
