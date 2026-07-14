#!/usr/bin/env python3
"""Validate a project's agent documentation without modifying the project."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


@dataclass(frozen=True)
class DocumentationPaths:
    agents: Path = Path("AGENTS.md")
    vision: Path = Path("docs/VISION.md")
    architecture: Path = Path("docs/ARCHITECTURE.md")
    abstractions: Path = Path("docs/ABSTRACTIONS.md")
    getting_started: Path = Path("docs/GETTING-STARTED.md")
    adr_directory: Path = Path("docs/adr")

    @property
    def adr_readme(self) -> Path:
        return self.adr_directory / "README.md"

    @property
    def core_documents(self) -> tuple[Path, ...]:
        return (
            self.agents,
            self.vision,
            self.architecture,
            self.abstractions,
            self.getting_started,
            self.adr_readme,
        )

    @property
    def agent_references(self) -> tuple[Path, ...]:
        return tuple(path for path in self.core_documents if path != self.agents)


DEFAULT_DOCUMENTATION_PATHS = DocumentationPaths()
COMPATIBILITY_DOCUMENTS = (Path("CLAUDE.md"), Path("GEMINI.md"))
PLACEHOLDER_PATTERNS = (
    re.compile(r"\{\{[^{}\r\n]+\}\}"),
    re.compile(r"\[TODO:[^\]\r\n]+\]", re.IGNORECASE),
    re.compile(r"<(?:PROJECT|APP|REPOSITORY)_[A-Z0-9_]+>"),
)
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
ADR_FILENAME_PATTERN = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
ADR_STATUS_PATTERN = re.compile(
    r"^(?:[-*]\s*)?(?:status|状态)\s*[:：]\s*"
    r"(?:proposed|active|superseded|retired)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
ADR_SECTION_PATTERNS = {
    "Context/背景": re.compile(
        r"^##\s+(?:Context|背景|上下文)\s*$", re.IGNORECASE | re.MULTILINE
    ),
    "Decision/决策": re.compile(
        r"^##\s+(?:Decision|决策)\s*$", re.IGNORECASE | re.MULTILINE
    ),
    "Options considered/考虑的方案": re.compile(
        r"^##\s+(?:Options considered|考虑的方案|备选方案)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "Consequences/影响": re.compile(
        r"^##\s+(?:Consequences|影响|后果)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
}


def project_relative_path(value: str) -> Path:
    normalized = value.strip()
    path = Path(normalized)
    looks_like_windows_absolute = re.match(r"^[a-zA-Z]:[\\/]", normalized)
    if not normalized:
        raise argparse.ArgumentTypeError("path must not be empty")
    if (
        path.is_absolute()
        or looks_like_windows_absolute
        or normalized.startswith("\\\\")
    ):
        raise argparse.ArgumentTypeError("path must be relative to the project root")
    if ".." in path.parts:
        raise argparse.ArgumentTypeError("path must not leave the project root")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate agent documentation at configurable project-relative paths."
    )
    parser.add_argument("project_root", type=Path, help="Path to the project root")
    parser.add_argument(
        "--agents-path",
        type=project_relative_path,
        default=DEFAULT_DOCUMENTATION_PATHS.agents,
        help="Agent instruction file relative to the project root (default: AGENTS.md)",
    )
    parser.add_argument(
        "--vision-path",
        type=project_relative_path,
        default=DEFAULT_DOCUMENTATION_PATHS.vision,
        help="Vision document relative to the project root (default: docs/VISION.md)",
    )
    parser.add_argument(
        "--architecture-path",
        type=project_relative_path,
        default=DEFAULT_DOCUMENTATION_PATHS.architecture,
        help=(
            "Architecture document relative to the project root "
            "(default: docs/ARCHITECTURE.md)"
        ),
    )
    parser.add_argument(
        "--abstractions-path",
        type=project_relative_path,
        default=DEFAULT_DOCUMENTATION_PATHS.abstractions,
        help=(
            "Abstractions document relative to the project root "
            "(default: docs/ABSTRACTIONS.md)"
        ),
    )
    parser.add_argument(
        "--getting-started-path",
        type=project_relative_path,
        default=DEFAULT_DOCUMENTATION_PATHS.getting_started,
        help=(
            "Getting-started document relative to the project root "
            "(default: docs/GETTING-STARTED.md)"
        ),
    )
    parser.add_argument(
        "--adr-dir",
        type=project_relative_path,
        default=DEFAULT_DOCUMENTATION_PATHS.adr_directory,
        help="ADR directory relative to the project root (default: docs/adr)",
    )
    return parser.parse_args()


def documentation_paths_from_args(args: argparse.Namespace) -> DocumentationPaths:
    return DocumentationPaths(
        agents=args.agents_path,
        vision=args.vision_path,
        architecture=args.architecture_path,
        abstractions=args.abstractions_path,
        getting_started=args.getting_started_path,
        adr_directory=args.adr_dir,
    )


def resolve_project_path(project_root: Path, relative_path: Path) -> Path:
    resolved_root = project_root.resolve()
    resolved_path = (resolved_root / relative_path).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"path leaves the project root: {relative_path}") from error
    return resolved_path


def validate_path_configuration(
    project_root: Path, documentation_paths: DocumentationPaths
) -> list[str]:
    errors: list[str] = []
    core_documents = documentation_paths.core_documents
    if len(set(core_documents)) != len(core_documents):
        errors.append("configured core document paths must be unique")
    for relative_path in (*core_documents, documentation_paths.adr_directory):
        try:
            resolve_project_path(project_root, relative_path)
        except ValueError as error:
            errors.append(str(error))
    return errors


def read_utf8(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        errors.append(f"{path}: is not valid UTF-8 ({error})")
    except OSError as error:
        errors.append(f"{path}: could not be read ({error})")
    return None


def strip_fenced_code(text: str) -> str:
    output: list[str] = []
    fence: str | None = None

    for line in text.splitlines():
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in {"```", "~~~"}:
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            output.append("")
            continue
        if fence is None:
            output.append(line)
        else:
            output.append("")

    return "\n".join(output)


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    elif " " in target:
        target = target.split(" ", 1)[0]
    return unquote(target).replace("\\", "/")


def is_external_or_anchor(target: str) -> bool:
    lowered = target.lower()
    return (
        not target
        or target.startswith("#")
        or lowered.startswith(("http://", "https://", "mailto:", "tel:", "data:"))
    )


def resolve_local_link(project_root: Path, source: Path, target: str) -> Path:
    path_part = target.split("#", 1)[0].split("?", 1)[0]
    if path_part.startswith("/"):
        return project_root / path_part.lstrip("/")
    return source.parent / path_part


def validate_placeholders(path: Path, text: str, errors: list[str]) -> None:
    searchable = strip_fenced_code(text)
    for pattern in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(searchable):
            line_number = searchable.count("\n", 0, match.start()) + 1
            errors.append(
                f"{path}:{line_number}: unresolved placeholder {match.group(0)!r}"
            )


def validate_links(
    project_root: Path, path: Path, text: str, errors: list[str]
) -> None:
    searchable = strip_fenced_code(text)
    for match in MARKDOWN_LINK_PATTERN.finditer(searchable):
        target = normalize_link_target(match.group(1))
        if is_external_or_anchor(target):
            continue
        resolved = resolve_local_link(project_root, path, target)
        if not resolved.exists():
            line_number = searchable.count("\n", 0, match.start()) + 1
            errors.append(
                f"{path}:{line_number}: local link target does not exist: {target}"
            )


def validate_agents_index(
    project_root: Path,
    path: Path,
    text: str,
    references: tuple[Path, ...],
    errors: list[str],
) -> None:
    linked_paths = resolved_local_links(project_root, path, text)
    for reference in references:
        normalized_reference = reference.as_posix()
        expected_path = resolve_project_path(project_root, reference)
        if normalized_reference not in text and expected_path not in linked_paths:
            errors.append(f"{path}: does not reference {normalized_reference}")


def resolved_local_links(project_root: Path, source: Path, text: str) -> set[Path]:
    linked_paths: set[Path] = set()
    searchable = strip_fenced_code(text)
    for match in MARKDOWN_LINK_PATTERN.finditer(searchable):
        target = normalize_link_target(match.group(1))
        if is_external_or_anchor(target):
            continue
        linked_paths.add(resolve_local_link(project_root, source, target).resolve())
    return linked_paths


def validate_compatibility_document(
    project_root: Path,
    relative_path: Path,
    agents_path: Path,
    errors: list[str],
) -> None:
    path = project_root / relative_path
    if not path.exists():
        return
    text = read_utf8(path, errors)
    if text is None:
        return
    normalized_agents_path = agents_path.as_posix()
    expected_agents_path = resolve_project_path(project_root, agents_path)
    linked_paths = resolved_local_links(project_root, path, text)
    if (
        normalized_agents_path not in text
        and expected_agents_path not in linked_paths
    ):
        errors.append(
            f"{path}: compatibility document does not reference {normalized_agents_path}"
        )
    validate_placeholders(path, text, errors)
    validate_links(project_root, path, text, errors)


def validate_adr(path: Path, text: str, errors: list[str]) -> None:
    if ADR_FILENAME_PATTERN.fullmatch(path.name) is None:
        errors.append(
            f"{path}: ADR filename must use NNNN-short-title.md with lowercase words"
        )
    if ADR_STATUS_PATTERN.search(text) is None:
        errors.append(
            f"{path}: ADR status must be proposed, active, superseded, or retired"
        )
    for label, pattern in ADR_SECTION_PATTERNS.items():
        if pattern.search(text) is None:
            errors.append(f"{path}: missing ADR section {label}")


def validate_document(
    project_root: Path,
    path: Path,
    errors: list[str],
    *,
    references: tuple[Path, ...] | None = None,
    is_adr: bool = False,
) -> None:
    text = read_utf8(path, errors)
    if text is None:
        return
    if not text.strip():
        errors.append(f"{path}: document is empty")
        return
    validate_placeholders(path, text, errors)
    validate_links(project_root, path, text, errors)
    if references is not None:
        validate_agents_index(project_root, path, text, references, errors)
    if is_adr:
        validate_adr(path, text, errors)


def validate_project(
    project_root: Path,
    documentation_paths: DocumentationPaths = DEFAULT_DOCUMENTATION_PATHS,
) -> list[str]:
    errors: list[str] = []
    project_root = project_root.expanduser().resolve()
    if not project_root.is_dir():
        return [f"{project_root}: project root is not a directory"]

    path_errors = validate_path_configuration(project_root, documentation_paths)
    if path_errors:
        return path_errors

    resolved_core_paths = {
        resolve_project_path(project_root, relative_path)
        for relative_path in documentation_paths.core_documents
    }
    for relative_path in documentation_paths.core_documents:
        path = resolve_project_path(project_root, relative_path)
        if not path.is_file():
            errors.append(f"{path}: required document is missing")
            continue
        references = None
        if relative_path == documentation_paths.agents:
            references = documentation_paths.agent_references
        validate_document(project_root, path, errors, references=references)

    adr_directory = resolve_project_path(
        project_root, documentation_paths.adr_directory
    )
    if adr_directory.is_dir():
        for path in sorted(adr_directory.glob("*.md")):
            if path.resolve() in resolved_core_paths:
                continue
            validate_document(project_root, path, errors, is_adr=True)

    for relative_path in COMPATIBILITY_DOCUMENTS:
        validate_compatibility_document(
            project_root, relative_path, documentation_paths.agents, errors
        )

    return errors


def main() -> int:
    args = parse_args()
    project_root = args.project_root.expanduser().resolve()
    documentation_paths = documentation_paths_from_args(args)
    errors = validate_project(project_root, documentation_paths)

    if errors:
        print(f"Agent documentation validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Agent documentation validation passed: {project_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
