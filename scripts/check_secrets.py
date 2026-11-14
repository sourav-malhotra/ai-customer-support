#!/usr/bin/env python3
"""Pre-commit security scanner to prevent committing secrets or credentials."""

import re
import subprocess
import sys

# High-confidence regex patterns for known credential types
SECRET_PATTERNS = [
    (
        "Google OAuth Client Secret",
        re.compile(r"GOCSPX-[A-Za-z0-9_-]{20,}"),
    ),
    (
        "Google OAuth Refresh Token",
        re.compile(r"1//0[A-Za-z0-9_-]{20,}"),
    ),
    (
        "Anthropic API Key",
        re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    ),
    (
        "OpenAI API Key",
        re.compile(r"sk-[A-Za-z0-9_-]{30,}"),
    ),
    (
        "Private Key Header",
        re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?KEY-----"),
    ),
]

# Sensitive keys in .env.example or template files that must remain empty or placeholders
SENSITIVE_ENV_KEYS = {
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "DATABASE_URL",
    "DASHBOARD_PASSWORD",
}

PLACEHOLDER_REGEX = re.compile(
    r"^(?:<[^>]+>|your[-_].*|placeholder|example|dummy|xxx+|changeme)?$",
    re.IGNORECASE,
)

FORBIDDEN_FILE_PATTERNS = [
    re.compile(r"^\.env(?!\.example$)"),
    re.compile(r"^credentials.*\.json$"),
    re.compile(r"^client_secret.*\.json$"),
    re.compile(r"^token.*\.json$"),
    re.compile(r".*\.(?:pem|key|p12|pfx)$"),
]


def run_git(*args: str) -> str:
    res = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        return ""
    return res.stdout


def check_staged_filenames() -> list[str]:
    violations = []
    staged_files = run_git("diff", "--cached", "--name-only").splitlines()
    for filepath in staged_files:
        filename = filepath.split("/")[-1].split("\\")[-1]
        for pattern in FORBIDDEN_FILE_PATTERNS:
            if pattern.search(filename):
                violations.append(
                    f"Forbidden secret file staged: '{filepath}' (matches pattern '{pattern.pattern}')"
                )
    return violations


def check_env_example_content() -> list[str]:
    """Ensure .env.example contains only blank placeholders for sensitive keys."""
    violations = []
    try:
        content = run_git("show", ":.env.example")
    except Exception:
        return violations

    for line_num, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip("'\"")
            if key in SENSITIVE_ENV_KEYS and val:
                if not PLACEHOLDER_REGEX.match(val):
                    violations.append(
                        f".env.example:line {line_num}: Sensitive key '{key}' has a populated value. "
                        f"Template files must have blank values or generic placeholders."
                    )
    return violations


def check_staged_diff() -> list[str]:
    violations = []
    diff_output = run_git("diff", "--cached", "-U0")
    current_file = "unknown"

    for line in diff_output.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue
        # Only check added or modified lines
        if line.startswith("+") and not line.startswith("+++"):
            added_content = line[1:]
            for label, pattern in SECRET_PATTERNS:
                match = pattern.search(added_content)
                if match:
                    matched_secret = match.group(0)
                    redacted = matched_secret[:6] + "..." + matched_secret[-4:]
                    violations.append(
                        f"Potential secret in '{current_file}': Detected {label} pattern ({redacted})"
                    )

    return violations


def main() -> int:
    violations = []
    violations.extend(check_staged_filenames())
    violations.extend(check_env_example_content())
    violations.extend(check_staged_diff())

    if violations:
        print("\n" + "=" * 76, file=sys.stderr)
        print("[BLOCKED] COMMIT ABORTED: SENSITIVE CREDENTIALS DETECTED", file=sys.stderr)
        print("=" * 76, file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print("-" * 76, file=sys.stderr)
        print("Fix instructions:", file=sys.stderr)
        print("  1. Store real credentials in '.env' (which is excluded by .gitignore).", file=sys.stderr)
        print("  2. Keep '.env.example' with empty values (e.g. KEY=).", file=sys.stderr)
        print("  3. Never stage files containing API keys, OAuth secrets, or tokens.", file=sys.stderr)
        print("=" * 76 + "\n", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
