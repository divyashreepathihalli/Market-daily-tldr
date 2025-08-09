# Market-daily-tldr
Get daily market TLDR 

## Market Daily TL;DR Emailer

A simple Python script that queries OpenAI for a daily market summary and emails the result. Two GitHub Actions workflows are included: one for USA at 6 AM Pacific, and one for India at 6 AM IST.

### 1) Local setup

- Python 3.11 recommended
- Create venv and install dependencies:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

- Create your `.env` (do NOT commit this file):
  ```ini
  OPENAI_API_KEY=sk-proj-...
  GMAIL_USERNAME=you@gmail.com
  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
  EMAIL_FROM_NAME=Market Daily TL;DR
  # Optional: if empty, defaults to GMAIL_USERNAME
  EMAIL_FROM_ADDRESS=
  # Comma-separated recipients
  DEFAULT_RECIPIENTS=alice@example.com,bob@example.com
  # Optional custom prefix (workflows force region-specific prefixes)
  SUBJECT_PREFIX=
  # Optional: custom disclaimer HTML (if empty, defaults provided)
  DISCLAIMER_HTML=
  ```

- Dry-run without sending:
  ```bash
  python3 daily_emailer.py --dry-run
  ```

- Send for real locally:
  ```bash
  python3 daily_emailer.py
  ```

### 2) GitHub Actions (production)

Because `.env` files are never committed, the workflows read a single secret that contains your environment variables.

- In your repo, go to Settings → Secrets and variables → Actions → New repository secret
- Name the secret: `DAILY_TLDR_ENV`
- Value: paste your `.env` contents (one KEY=VALUE per line), for example:
  ```ini
  OPENAI_API_KEY=sk-proj-...
  GMAIL_USERNAME=you@gmail.com
  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
  EMAIL_FROM_NAME=Market Daily TL;DR
  EMAIL_FROM_ADDRESS=you@gmail.com
  DEFAULT_RECIPIENTS=alice@example.com,bob@example.com
  # Optional
  SUBJECT_PREFIX=
  DISCLAIMER_HTML=
  ```

The workflows will write this secret to `.env` on the runner and then set region-specific variables as needed.

### 3) Workflows

- USA: `.github/workflows/daily-email.yml`
  - Runs every day at 06:00 Pacific (DST-aware via UTC schedules + guard)
  - Reuses `DAILY_TLDR_ENV`
  - Forces `SUBJECT_PREFIX=Market Daily TL;DR USA`
  - Sets `FOCUS_MARKET=United States (...)` to steer the prompt

- India: `.github/workflows/daily-email-india.yml`
  - Runs every day at 06:00 IST (cron: `30 0 * * *` UTC)
  - Reuses `DAILY_TLDR_ENV` (no second secret required)
  - Forces `SUBJECT_PREFIX=Market Daily TL;DR (India)`
  - Sets `FOCUS_MARKET=India (...)` to steer the prompt

### 4) Sending model output as-is

- The script sends the model’s HTML output as-is. A disclaimer is appended automatically.
- You can override the disclaimer with `DISCLAIMER_HTML`.

### 5) Running manually from Actions

- Go to Actions → select a workflow (USA or India) → Run workflow.
- Logs will show the region focus line.

### 6) Notes

- Keep `.env` out of git; `.gitignore` is configured accordingly.
- To change recipients: update `DEFAULT_RECIPIENTS` locally and in `DAILY_TLDR_ENV` secret.
- To test region focus locally:
  ```bash
  FOCUS_MARKET="United States" python3 daily_emailer.py --dry-run
  FOCUS_MARKET="India" python3 daily_emailer.py --dry-run
  ``` 
