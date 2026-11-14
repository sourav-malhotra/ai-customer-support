# Workspace Rules & Development Protocols

## Git Commit Protocol
- **Commit After Every Change**: After completing each discrete change, feature addition, bug fix, configuration update, or file modification, immediately stage the changed files and create a Git commit.
- **Commit Message Format**: Use Conventional Commits formatting (e.g., `feat: ...`, `fix: ...`, `docs: ...`, `chore: ...`, `refactor: ...`, `test: ...`). Make commit messages concise and descriptive.
- **Safety First (Strict Secret Zero-Tolerance)**:
  - Never commit secrets, credentials, API keys, or tokens under any circumstance.
  - Active credentials must ONLY be stored in `.env` (which is excluded by `.gitignore`).
  - Template and example files like `.env.example` must ONLY contain blank values or generic placeholders (e.g., `GOOGLE_CLIENT_SECRET=`).
  - Never track or stage files matching `.gitignore` (such as `.env`, `credentials.json`, `client_secret*.json`, `token*.json`, `.venv/`, `__pycache__/`).
  - Before committing, verify with the pre-commit scanner (`python scripts/check_secrets.py`) that no secrets are staged.
