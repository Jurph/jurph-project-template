#!/usr/bin/env python3
"""Create a new project repo from this template."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


PLACEHOLDER_PACKAGE = "your_project"
PLACEHOLDER_SCRIPT = "your-project"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a new sibling project from this template, initialize git, "
            "and rewrite the obvious placeholders."
        )
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        help="Name of the new project folder and display name, for example 'finnegan'.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the target folder if it already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without writing files.",
    )
    return parser


def slugify_script_name(project_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")
    return slug or "new-project"


def slugify_package_name(project_name: str) -> str:
    package = re.sub(r"[^a-z0-9]+", "_", project_name.lower()).strip("_")
    if not package:
        package = "new_project"
    if package[0].isdigit():
        package = f"project_{package}"
    return package


def title_case_name(project_name: str) -> str:
    return re.sub(r"[-_]+", " ", project_name).strip().title()


def should_skip(path: Path) -> bool:
    skipped_names = {
        ".git",
        ".venv",
        "venv",
        ".uv-cache",
        ".uv-python",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "uv.lock",
    }
    return any(part in skipped_names for part in path.parts)


def rewrite_text_file(path: Path, display_name: str, package_name: str, script_name: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(PLACEHOLDER_PACKAGE, package_name)
    text = text.replace(PLACEHOLDER_SCRIPT, script_name)

    if path.name == "README.md":
        lines = text.splitlines()
        if lines and lines[0].startswith("# "):
            lines[0] = f"# {display_name}"
        if len(lines) > 2 and "boring-on-purpose Python starter repo" in lines[2]:
            lines[2] = f"{display_name} is a project to [TODO]."
        text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")

    path.write_text(text, encoding="utf-8")


def init_git_repo(target_dir: Path) -> None:
    subprocess.run(["git", "init"], cwd=target_dir, check=True)


def copy_template(template_dir: Path, target_dir: Path) -> None:
    shutil.copytree(
        template_dir,
        target_dir,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            "venv",
            ".uv-cache",
            ".uv-python",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "uv.lock",
            "deploy.py",
        ),
    )


def deploy_project(project_name: str, force: bool, dry_run: bool) -> Path:
    template_dir = Path(__file__).resolve().parent
    parent_dir = template_dir.parent
    target_dir = parent_dir / project_name
    package_name = slugify_package_name(project_name)
    script_name = slugify_script_name(project_name)
    display_name = title_case_name(project_name)

    if target_dir.exists():
        if not force:
            raise FileExistsError(f"Target directory already exists: {target_dir}")
        if not dry_run:
            shutil.rmtree(target_dir)

    print(f"Template: {template_dir}")
    print(f"Target:   {target_dir}")
    print(f"Package:  {package_name}")
    print(f"Script:   {script_name}")

    if dry_run:
        print("Dry run only. No files were written.")
        return target_dir

    copy_template(template_dir, target_dir)

    src_placeholder = target_dir / "src" / PLACEHOLDER_PACKAGE
    src_actual = target_dir / "src" / package_name
    src_placeholder.rename(src_actual)

    for path in target_dir.rglob("*"):
        if should_skip(path) or path.is_dir():
            continue
        if path.suffix in {".py", ".md", ".toml", ".txt"}:
            rewrite_text_file(path, display_name, package_name, script_name)

    init_git_repo(target_dir)
    return target_dir


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.project_name:
        parser.print_help()
        return 0

    try:
        target_dir = deploy_project(
            project_name=args.project_name,
            force=args.force,
            dry_run=args.dry_run,
        )
    except FileExistsError as exc:
        print(exc, file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        print(f"Git initialization failed: {exc}", file=sys.stderr)
        return exc.returncode

    print(f"Created new project at {target_dir}")
    print("Next steps:")
    print(f"  cd {target_dir.name}")
    print("  uv sync --extra dev")
    print("  uv run pytest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
