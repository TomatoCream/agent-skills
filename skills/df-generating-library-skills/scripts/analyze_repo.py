#!/usr/bin/env python3
"""
Repository Analyzer for Library Skill Generation.

Scans a repository and produces a structured manifest identifying:
- Library identity (name, language, version, build system)
- Documentation sources
- Public API surface
- Test locations
- Gotcha indicators (warning comments, deprecated APIs, thread-safety notes)

Usage:
    python3 analyze_repo.py <repo_path> [--output <path>]

Output: JSON manifest to stdout (or file if --output specified)
"""

import json
import re
import sys
from pathlib import Path


def detect_build_system(repo: Path) -> dict:
    """Detect build system and extract metadata."""
    result = {"system": "unknown", "language": "unknown", "metadata": {}}

    # Java - Maven
    pom = repo / "pom.xml"
    if pom.exists():
        content = pom.read_text(errors="replace")
        result["system"] = "maven"
        result["language"] = "java"
        # Extract coordinates
        group = re.search(r"<groupId>([^<]+)</groupId>", content)
        artifact = re.search(r"<artifactId>([^<]+)</artifactId>", content)
        version = re.search(r"<version>([^<]+)</version>", content)
        if group:
            result["metadata"]["groupId"] = group.group(1)
        if artifact:
            result["metadata"]["artifactId"] = artifact.group(1)
        if version:
            result["metadata"]["version"] = version.group(1)
        return result

    # Java - Gradle
    for gradle_file in ["build.gradle", "build.gradle.kts"]:
        gf = repo / gradle_file
        if gf.exists():
            result["system"] = "gradle"
            result["language"] = "java"
            content = gf.read_text(errors="replace")
            version = re.search(r"""version\s*[=:]\s*['"]([^'"]+)['"]""", content)
            group = re.search(r"""group\s*[=:]\s*['"]([^'"]+)['"]""", content)
            if version:
                result["metadata"]["version"] = version.group(1)
            if group:
                result["metadata"]["groupId"] = group.group(1)
            return result

    # JavaScript/TypeScript - npm
    pkg = repo / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            result["system"] = "npm"
            result["language"] = "typescript" if (repo / "tsconfig.json").exists() else "javascript"
            result["metadata"]["name"] = data.get("name", "")
            result["metadata"]["version"] = data.get("version", "")
            result["metadata"]["main"] = data.get("main", "")
            result["metadata"]["module"] = data.get("module", "")
        except json.JSONDecodeError:
            pass
        return result

    # Python - pyproject.toml
    pyproject = repo / "pyproject.toml"
    if pyproject.exists():
        result["system"] = "pyproject"
        result["language"] = "python"
        content = pyproject.read_text(errors="replace")
        name = re.search(r'name\s*=\s*"([^"]+)"', content)
        version = re.search(r'version\s*=\s*"([^"]+)"', content)
        if name:
            result["metadata"]["name"] = name.group(1)
        if version:
            result["metadata"]["version"] = version.group(1)
        return result

    # Python - setup.py
    setup = repo / "setup.py"
    if setup.exists():
        result["system"] = "setuptools"
        result["language"] = "python"
        content = setup.read_text(errors="replace")
        name = re.search(r"""name\s*=\s*['"]([^'"]+)['"]""", content)
        if name:
            result["metadata"]["name"] = name.group(1)
        return result

    # Go
    gomod = repo / "go.mod"
    if gomod.exists():
        result["system"] = "go-modules"
        result["language"] = "go"
        content = gomod.read_text(errors="replace")
        module = re.search(r"module\s+(.+)", content)
        go_ver = re.search(r"go\s+([\d.]+)", content)
        if module:
            result["metadata"]["module"] = module.group(1).strip()
        if go_ver:
            result["metadata"]["goVersion"] = go_ver.group(1)
        return result

    # Rust
    cargo = repo / "Cargo.toml"
    if cargo.exists():
        result["system"] = "cargo"
        result["language"] = "rust"
        content = cargo.read_text(errors="replace")
        name = re.search(r'name\s*=\s*"([^"]+)"', content)
        version = re.search(r'version\s*=\s*"([^"]+)"', content)
        if name:
            result["metadata"]["name"] = name.group(1)
        if version:
            result["metadata"]["version"] = version.group(1)
        return result

    return result


def find_documentation(repo: Path) -> list:
    """Find all documentation sources in the repo."""
    docs = []
    # Check explicit files
    for name in ["README.md", "README.rst", "README.txt", "README",
                 "CHANGELOG.md", "CHANGELOG.rst", "CHANGES.md", "HISTORY.md",
                 "CONTRIBUTING.md", "MIGRATION.md", "UPGRADING.md"]:
        f = repo / name
        if f.exists():
            size = f.stat().st_size
            docs.append({"path": str(f.relative_to(repo)), "type": "root-doc", "size": size})

    # Check doc directories
    for dirname in ["docs", "doc", "documentation", "wiki", "guide", "guides"]:
        d = repo / dirname
        if d.is_dir():
            for f in d.rglob("*.md"):
                size = f.stat().st_size
                docs.append({"path": str(f.relative_to(repo)), "type": "doc-dir", "size": size})
            for f in d.rglob("*.rst"):
                size = f.stat().st_size
                docs.append({"path": str(f.relative_to(repo)), "type": "doc-dir", "size": size})
            for f in d.rglob("*.adoc"):
                size = f.stat().st_size
                docs.append({"path": str(f.relative_to(repo)), "type": "doc-dir", "size": size})

    return docs


def find_source_structure(repo: Path, language: str) -> dict:
    """Map the source code structure."""
    structure = {"source_roots": [], "packages": [], "key_files": [], "total_files": 0}

    ext_map = {
        "java": ".java",
        "javascript": ".js",
        "typescript": ".ts",
        "python": ".py",
        "go": ".go",
        "rust": ".rs",
    }
    ext = ext_map.get(language, ".*")

    # Find source roots
    for root_candidate in ["src/main/java", "src/main", "src", "lib", "pkg"]:
        r = repo / root_candidate
        if r.is_dir():
            structure["source_roots"].append(root_candidate)

    # Count files and find packages
    packages = set()
    all_files = []
    for root_dir in structure["source_roots"] or ["."]:
        base = repo / root_dir
        if not base.is_dir():
            continue
        for f in base.rglob(f"*{ext}"):
            if any(skip in str(f) for skip in ["/test/", "/tests/", "__test__", ".test.", "_test.", "node_modules", ".git"]):
                continue
            rel = f.relative_to(base)
            all_files.append(str(rel))
            # Extract package/directory
            if rel.parent != Path("."):
                packages.add(str(rel.parent))

    structure["packages"] = sorted(packages)[:50]  # Cap at 50
    structure["total_files"] = len(all_files)

    # Identify key files (entry points, configs, main classes)
    key_patterns = [
        r"(^|/)index\.", r"(^|/)main\.", r"(^|/)app\.",
        r"(^|/)client\.", r"(^|/)config\.", r"(^|/)pool\.",
        r"(^|/)connection\.", r"(^|/)factory\.",
        r"Config\.", r"Builder\.", r"Options\.", r"Exception\.",
    ]
    for f in all_files:
        for pat in key_patterns:
            if re.search(pat, f, re.IGNORECASE):
                structure["key_files"].append(f)
                break

    structure["key_files"] = structure["key_files"][:30]  # Cap at 30
    return structure


def find_tests(repo: Path, _language: str) -> dict:
    """Find test files and patterns."""
    tests = {"locations": [], "total_files": 0, "sample_files": []}

    _ = {  # noqa: F841 - available for future language-specific filtering
        "java": "*.java",
        "javascript": "*.{js,ts}",
        "typescript": "*.{js,ts}",
        "python": "*.py",
        "go": "*_test.go",
        "rust": "*.rs",
    }

    test_dirs = ["src/test", "test", "tests", "__tests__", "spec"]
    for td in test_dirs:
        d = repo / td
        if d.is_dir():
            tests["locations"].append(td)
            count = sum(1 for _ in d.rglob("*") if _.is_file() and not _.name.startswith("."))
            tests["total_files"] += count
            # Get a few sample test files
            samples = list(d.rglob("*.java")) + list(d.rglob("*.py")) + list(d.rglob("*.ts")) + list(d.rglob("*.js")) + list(d.rglob("*.go"))
            for s in samples[:5]:
                tests["sample_files"].append(str(s.relative_to(repo)))

    return tests


def find_gotcha_indicators(repo: Path, language: str) -> dict:
    """Search for warning comments and gotcha indicators in source code."""
    indicators = {"warnings": [], "deprecations": [], "thread_safety": [], "total_count": 0}

    ext_map = {
        "java": "*.java",
        "javascript": "*.js",
        "typescript": "*.ts",
        "python": "*.py",
        "go": "*.go",
        "rust": "*.rs",
    }
    glob_pat = ext_map.get(language, "*.*")

    warning_patterns = [
        (r"(?i)(WARNING|CAUTION|IMPORTANT|FIXME|HACK|XXX)[:!\s]", "warning"),
        (r"@Deprecated|#\[deprecated\]|warnings\.warn.*Deprecat", "deprecation"),
        (r"(?i)(thread.?safe|not.?thread.?safe|synchronized|mutex|lock|atomic|concurrent)", "thread_safety"),
        (r"(?i)(do\s+not|must\s+not|never|always\s+close|always\s+release|memory\s+leak)", "gotcha"),
    ]

    source_dirs = ["src", "lib", "pkg"]
    search_dirs = [repo / d for d in source_dirs if (repo / d).is_dir()]
    if not search_dirs:
        search_dirs = [repo]

    for search_dir in search_dirs:
        for f in search_dir.rglob(glob_pat):
            if any(skip in str(f) for skip in ["/test/", "/tests/", "node_modules", ".git", "vendor"]):
                continue
            try:
                content = f.read_text(errors="replace")
                for pattern, category in warning_patterns:
                    for match in re.finditer(pattern, content):
                        # Get the line
                        line_start = content.rfind("\n", 0, match.start()) + 1
                        line_end = content.find("\n", match.end())
                        if line_end == -1:
                            line_end = len(content)
                        line = content[line_start:line_end].strip()
                        line_num = content[:match.start()].count("\n") + 1

                        entry = {
                            "file": str(f.relative_to(repo)),
                            "line": line_num,
                            "category": category,
                            "text": line[:200],  # Cap line length
                        }

                        if category == "deprecation":
                            indicators["deprecations"].append(entry)
                        elif category == "thread_safety":
                            indicators["thread_safety"].append(entry)
                        else:
                            indicators["warnings"].append(entry)
                        indicators["total_count"] += 1
            except (OSError, UnicodeDecodeError):
                continue

    # Cap results to prevent huge output
    indicators["warnings"] = indicators["warnings"][:30]
    indicators["deprecations"] = indicators["deprecations"][:20]
    indicators["thread_safety"] = indicators["thread_safety"][:20]

    return indicators


def estimate_popularity(repo: Path) -> dict:
    """Estimate library popularity tier."""
    result = {"tier": "unknown", "stars": None, "evidence": []}

    # Check if it's a git repo with a GitHub remote
    git_config = repo / ".git" / "config"
    if git_config.exists():
        content = git_config.read_text(errors="replace")
        github_match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", content)
        if github_match:
            result["evidence"].append(f"GitHub repo: {github_match.group(1)}/{github_match.group(2)}")
            result["github_owner"] = github_match.group(1)
            result["github_repo"] = github_match.group(2).rstrip(".git")

        gitlab_match = re.search(r"gitlab\.com[:/]([^/]+)/([^/.]+)", content)
        if gitlab_match:
            result["evidence"].append(f"GitLab repo: {gitlab_match.group(1)}/{gitlab_match.group(2)}")

    return result


def analyze_repo(repo_path: str) -> dict:
    """Main analysis function."""
    repo = Path(repo_path).resolve()

    if not repo.is_dir():
        return {"error": f"Not a directory: {repo_path}"}

    build = detect_build_system(repo)
    docs = find_documentation(repo)
    source = find_source_structure(repo, build["language"])
    tests = find_tests(repo, build["language"])
    gotchas = find_gotcha_indicators(repo, build["language"])
    popularity = estimate_popularity(repo)

    # Determine library name
    name = (
        build["metadata"].get("artifactId")
        or build["metadata"].get("name")
        or build["metadata"].get("module", "").split("/")[-1]
        or repo.name
    )

    manifest = {
        "name": name,
        "path": str(repo),
        "build": build,
        "documentation": {
            "files": docs,
            "total_count": len(docs),
            "total_size_bytes": sum(d["size"] for d in docs),
        },
        "source": source,
        "tests": tests,
        "gotcha_indicators": gotchas,
        "popularity": popularity,
        "summary": {
            "language": build["language"],
            "build_system": build["system"],
            "source_files": source["total_files"],
            "doc_files": len(docs),
            "test_files": tests["total_files"],
            "gotcha_indicators_found": gotchas["total_count"],
            "key_files_count": len(source["key_files"]),
        },
    }

    return manifest


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_repo.py <repo_path> [--output <path>]", file=sys.stderr)
        sys.exit(1)

    repo_path = sys.argv[1]
    output_path = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    result = analyze_repo(repo_path)

    output = json.dumps(result, indent=2)

    if output_path:
        Path(output_path).write_text(output)
        print(f"Manifest written to {output_path}", file=sys.stderr)
    else:
        print(output)
