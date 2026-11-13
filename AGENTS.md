# Workspace Rules & Development Protocols

## Git Commit Protocol
- **Commit After Every Change**: After completing each discrete change, feature addition, bug fix, configuration update, or file modification, immediately stage the changed files and create a Git commit.
- **Commit Message Format**: Use Conventional Commits formatting (e.g., `feat: ...`, `fix: ...`, `docs: ...`, `chore: ...`, `refactor: ...`, `test: ...`). Make commit messages concise and descriptive.
- **Safety First**: Never commit secrets, credentials, API keys, or files matching `.gitignore` (such as `.env`, `credentials.json`, `.venv/`, `__pycache__/`).
