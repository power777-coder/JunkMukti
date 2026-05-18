# TODO - Make repo GitHub safe

- [ ] Update Django settings to remove hardcoded SECRET_KEY and make DEBUG/ALLOWED_HOSTS env-driven
- [ ] Update .gitignore to exclude db.sqlite3, staticfiles/, and ML artifacts (e.g., ml/*.pkl)
- [ ] Re-scan repo for common secret patterns to ensure no secrets remain
- [ ] (After edits) Run `python manage.py check` and `git status` to verify

