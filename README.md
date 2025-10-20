# linkedin-easy-apply

Automated script to find LinkedIn "Easy Apply" jobs and attempt automated applications using Playwright. This project is intended as a developer tool and comes with important legal/ethical considerations — read the Security & Ethics section below before contributing or using.

## Features
- Browse LinkedIn job search pages and collect "Easy Apply" jobs ([`utils.search.search_easy_apply_jobs`](utils/search.py))
- Attempt multi-step Easy Apply forms with heuristics for filling inputs, radios, selects, and file uploads ([`utils.apply.apply_easy_apply_job`](utils/apply.py), [`utils.apply.apply_for_jobs`](utils/apply.py))
- Human-like actions (delays, typing) to reduce detection ([`utils.humanize.random_sleep`](utils/humanize.py))
- Use a persistent Playwright context and saved session data to avoid repeated logins ([`utils.login.linkedin_login`](utils/login.py), [`utils.login.is_logged_in`](utils/login.py))
- Minimal in-memory application logging/data model ([`db.models.JobApplication`](db/models.py)) (TODO)

## Table of Contents
- Requirements
- Installation
- Configuration
- Usage
- Development / Code Structure
- Troubleshooting
- Security & Ethics
- Contributing
- License

## Requirements
- Python 3.10+ (project uses modern typing)
- Playwright (browser automation)
- PyYAML, python-dotenv

Suggested installs:
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

## Installation
1. Clone the repo.
2. Create and activate a Python virtual environment.
3. Install dependencies (see Requirements).
4. Configure environment and config files (see Configuration).

## Configuration
- `config.yaml` (not committed): project-level settings. See [sample-config.yaml](sample-config.yaml) for structure.
- `.env`: store credentials and personal information:
  - LINKEDIN_EMAIL
  - LINKEDIN_PASSWORD
  - RESUME_PATH (path to your resume file)
  - PHONE
  - EMAIL

Important: Keep `.env` and `config.yaml` out of version control (already in `.gitignore`).

Example config values are available in [sample-config.yaml](sample-config.yaml).

## Usage
Run the project from the repo root:

```sh
python main.py
```

What happens:
- The script opens a persistent Playwright context ([`main`](main.py)).
- It checks login status and will use the saved session in `user_data/` if available ([`utils.login.is_logged_in`](utils/login.py)). If the session expired, it will perform a login flow and attempt to save cookies.
- It searches the job listing page specified in your config via [`utils.search.search_easy_apply_jobs`](utils/search.py).
- It attempts to apply to collected jobs using [`utils.apply.apply_for_jobs`](utils/apply.py).

## Development / Code Structure
- main.py — entry point; orchestrates Playwright session and workflow ([main.py](main.py))
- utils/
  - login.py — login flows and cookie handling (`linkedin_login`, `is_logged_in`, `perform_login`) ([utils/login.py](utils/login.py))
  - humanize.py — human-like delays and helper actions (`random_sleep`, `human_type`, `human_click`) ([utils/humanize.py](utils/humanize.py))
  - search.py — job-list scraping / discovery (`search_easy_apply_jobs`) ([utils/search.py](utils/search.py))
  - apply.py — form detection and automated application logic (`apply_easy_apply_job`, `apply_for_jobs`) ([utils/apply.py](utils/apply.py))
  - logger.py — lightweight logger wrapper ([utils/logger.py](utils/logger.py))
- db/models.py — simple dataclass and in-memory store for applied jobs ([db/models.py](db/models.py))

If you extend or refactor, prefer small, testable functions and add unit tests for parsing/matching logic (e.g., `get_answer_for_question`).

## Troubleshooting
- Playwright errors: ensure `python -m playwright install` completed and browsers are installed.
- Login failures: ensure `.env` values are set and valid.
- No jobs found: check the `url` in your `config.yaml` and test manually in a browser to confirm the job list is visible.
- Cookie/session issues: remove `user_data/` and re-run to re-generate a fresh persistent context.

## Security & Ethics
- Respect LinkedIn's Terms of Service and local laws. Automating applications may violate ToS or employer systems.
- Do not store or commit credentials. `.gitignore` already excludes `.env` and `config.yaml`.
- Use this repository responsibly. This project is intended for learning and automation experiments; don't use it to spam or abuse job systems.

## Contributing
- Remove secrets before opening PRs.
- Write tests for parsing heuristics and form-handling changes.
- Add clear change descriptions and a rationale when modifying fill heuristics.

## License
Suggested: MIT. Add a LICENSE file when you decide.

## Useful references in this repo
- Entry: [`main`](main.py) — [main.py](main.py)
- Login: [`utils.login.linkedin_login`](utils/login.py) — [utils/login.py](utils/login.py)
- Search: [`utils.search.search_easy_apply_jobs`](utils/search.py) — [utils/search.py](utils/search.py)
- Apply: [`utils.apply.apply_for_jobs`](utils/apply.py) / [`utils.apply.apply_easy_apply_job`](utils/apply.py) — [utils/apply.py](utils/apply.py)
- Humanization utils: [`utils.humanize.random_sleep`](utils/humanize.py) — [utils/humanize.py](utils/humanize.py)
- Data model: [`db.models.JobApplication`](db/models.py) — [db/models.py](db/models.py)
