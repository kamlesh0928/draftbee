# DraftBee

DraftBee drafts LinkedIn posts for you and publishes them once you approve. It picks a topic, writes the post with Gemini, sends the draft to a private Discord channel, and posts it to LinkedIn only after you click **Accept**.

## How it works

```
 scheduler (every few days) ─┐
                             ├─► pick a topic ─► draft the post ─► Discord review ─► LinkedIn
 /generate in Discord       ─┘    (database,       (Gemini)        Accept / Reject /
                                   else Gemini)                     Re-try
```

1. **Pick a topic.** Unused ideas saved in the database are used first. Gemini is only called for new ideas when none are left, which keeps LLM calls low.
2. **Draft the post.** Gemini writes a LinkedIn post for the topic, hashtags included.
3. **Review on Discord.** The draft appears in your approval channel with three buttons:
   - **Accept**: publishes the post to LinkedIn and marks the topic as used.
   - **Reject**: marks the topic as rejected and moves on to the next one.
   - **Re-try**: writes a new draft for the same topic.
4. A draft with no response after one hour is treated as rejected.

Posting runs on a schedule (set in `app/scheduler/jobs.py`) and on demand with the `/generate` slash command.

## Tech stack

Python, discord.py, Google Gemini, FastAPI, SQLAlchemy, Alembic, PostgreSQL (Neon), APScheduler, httpx, tenacity.

## Setup

### Prerequisites

- Python 3.13+
- A PostgreSQL database (Neon works well)
- A Discord application with a bot, invited to your server with the `bot` and `applications.commands` scopes and the Send Messages and Embed Links permissions
- A Google Gemini API key
- A LinkedIn developer app with the **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect** products, verified against a LinkedIn Company Page

### Install

```bash
git clone <your-repo-url>
cd draftbee
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Configure

Create a `.env` file in the project root (it is gitignored):

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | yes | Postgres connection string (Neon needs `?sslmode=require`) |
| `DISCORD_BOT_TOKEN` | yes | Bot token from the Discord Developer Portal |
| `DISCORD_SERVER_ID` | yes | ID of your Discord server |
| `DISCORD_APPROVAL_CHANNEL_ID` | yes | Channel where drafts are posted for review |
| `GEMINI_API_KEY` | yes | Google Gemini API key |
| `GEMINI_MODEL` | yes | Gemini model name to use |
| `LINKEDIN_ACCESS_TOKEN` | yes | Access token from the authorize script (valid about 60 days) |
| `LINKEDIN_PERSON_ID` | yes | Your LinkedIn member ID |
| `LINKEDIN_API_VERSION` | yes | API version as `YYYYMM`, for example `202608` |
| `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REFRESH_TOKEN` | no | Not read by the app |
| `X_CLIENT_ID`, `X_CLIENT_SECRET`, `X_ACCESS_TOKEN`, `X_REFRESH_TOKEN` | no | Only needed if X posting is re-enabled |

Enable Developer Mode in Discord (User Settings → Advanced) to copy the server and channel IDs.

### Get LinkedIn credentials

```bash
python scripts/linkedin_authorize.py
```

It opens a browser for consent and prints the `LINKEDIN_*` lines to add to `.env`. The redirect URL `http://localhost:8080/callback` must be registered in your LinkedIn app. Repeat this when the token expires (about every 60 days).

### Set up the database

The tables already exist on the Neon database used so far. For a new, empty database, create them once:

```bash
python -c "from app.database.base import Base, engine; from app.database import models; Base.metadata.create_all(bind=engine)"
alembic stamp head
```

For later model changes: `alembic revision --autogenerate -m "describe the change"`, then `alembic upgrade head`.

## Running locally

```bash
python -m app.run_bot              # bot + scheduler
uvicorn app.main:app --port 5001   # bot + scheduler + /health endpoint
```

Run only one at a time. Then type `/generate` in your Discord server to create a draft.

## Development

```bash
pytest -v
ruff check .
mypy app --ignore-missing-imports
```

GitHub Actions runs the same three checks on every push and pull request.

## Deploying to Render (free)

Render's free tier has no Background Workers, so DraftBee runs as a free **Web Service** with an uptime monitor that keeps it awake.

1. New → Web Service, connect this repository.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Instance type: Free. Add the required variables from the table above, plus `PYTHON_VERSION`.
5. Create a free UptimeRobot monitor on `https://<service>.onrender.com/health` (every 5 minutes) so the service does not sleep.

Do not run a local copy with the same bot token while the deployed one is running.

## Posting to X (currently disabled)

X's API is pay-per-use, so X posting is switched off. The code is kept in `app/publishers/x.py`. To re-enable it, uncomment the lines marked "Uncomment - If added credits on X platform" in `app/agents/writer_agent.py` and `app/agents/orchestrator.py`, set the `X_*` variables (get them with `scripts/x_authorize.py`), and update the tests that have matching commented lines.

## Known limitations

- The schedule is held in memory, so the interval restarts whenever the service restarts.
- The LinkedIn access token must be renewed about every 60 days.
- Free hosting is not guaranteed to be always-on; if the uptime ping fails, the bot goes offline until the service wakes up.