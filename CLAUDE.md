# Prelegal Project

## Overview

This is a SaaS product to allow users to draft legal agreements based on templates in the templates directory.
The user can carry out AI chat in order to establish what document they want and how to fill in the fields.
The available documents are covered in the catalog.json file in the project root, included here:

@catalog.json

The current implementation has the V1 technical foundation in place (FastAPI backend, SQLite, Docker, auth API) and a Mutual NDA form prototype in the frontend. AI chat, document persistence, and auth UI are not yet built.

## Development process

When instructed to build a feature:
1. Use your Atlassian tools to read the feature instructions from Jira
2. Develop the feature - do not skip any step from the feature-dev 7 step process
3. Thoroughly test the feature with unit tests and integration tests and fix any issues
4. Submit a PR using your github tools

## AI design

When writing code to make calls to LLMs, use your Cerebras skill to use LiteLLM via OpenRouter to the `openrouter/openai/gpt-oss-120b` model with Cerebras as the inference provider. You should use Structured Outputs so that you can interpret the results and populate fields in the legal document.

There is an OPENROUTER_API_KEY in the .env file in the project root.

## Technical design

The entire project should be packaged into a Docker container.
The backend should be in backend/ and be a uv project, using FastAPI.
The frontend should be in frontend/
The database should use SQLLite and be created from scratch each time the Docker container is brought up, allowing for a users table with sign up and sign in.
The frontend is statically built (`next.config.ts` uses `output: 'export'`) and served by FastAPI from `backend/static/`.
There should be scripts in scripts/ for:
```bash
# Mac
scripts/start-mac.sh    # Start
scripts/stop-mac.sh     # Stop

# Linux
scripts/start-linux.sh
scripts/stop-linux.sh

# Windows
scripts/start-windows.ps1
scripts/stop-windows.ps1
```
Backend available at http://localhost:8000

## Implementation status

| Area | Status | Notes |
|------|--------|-------|
| Templates | Done | 12 templates in `templates/`, catalogued in `catalog.json` |
| Frontend prototype | Done | Mutual NDA form in `frontend/` (Next.js, static export) |
| Backend foundation | Done | FastAPI + uv in `backend/`, served at port 8000 |
| Database | Done | SQLite, recreated fresh on each container startup |
| Auth API | Done | `POST /api/auth/signup` and `/signin` return JWT tokens |
| Docker + scripts | Done | `Dockerfile`, `docker-compose.yml`, and `scripts/` for Mac/Linux/Windows |
| Auth UI | Not started | Sign up / sign in screens not yet built |
| AI chat | Not started | LLM integration for document drafting not yet built |
| Document persistence | Not started | Saving/loading user documents not yet built |
| Full document support | Not started | Only Mutual NDA is wired up; the other 11 templates are not yet in the UI |

## Color Scheme
- Accent Yellow: `#ecad0a`
- Blue Primary: `#209dd7`
- Purple Secondary: `#753991` (submit buttons)
- Dark Navy: `#032147` (headings)
- Gray Text: `#888888`
