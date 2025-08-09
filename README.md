# Market-daily-tldr
Get daily market TLDR 

## Market Daily TL;DR Emailer

A simple Python script that fetches optional news context, queries OpenAI with a finance-focused prompt, and emails the HTML summary to a recipient list.

### Setup

1. Create and activate a virtual environment (recommended):
   
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy env template and fill in values:
   
   ```bash
   cp .env.example .env
   # edit .env
   ```

   Required:
   - `OPENAI_API_KEY`
   - Gmail App Password auth:
     - `GMAIL_USERNAME` (your Gmail address)
     - `GMAIL_APP_PASSWORD` (create at Google Account → Security → App passwords)
   - `DEFAULT_RECIPIENTS` (comma-separated)

   Optional:
   - `EMAIL_FROM_NAME` (default: Market Daily TL;DR)
   - `EMAIL_FROM_ADDRESS` (defaults to `GMAIL_USERNAME`)
   - `NEWSAPI_KEY` to include freshest headlines as context
   - `SUBJECT_PREFIX`

3. Add recipients, either via `--to`, a file, or `DEFAULT_RECIPIENTS`:
   
   ```bash
   cp recipients.example.txt recipients.txt
   # edit recipients.txt
   ```

### Run once (dry-run)

```bash
python3 daily_emailer.py --recipients recipients.txt --dry-run
```

### Send for real

```bash
python3 daily_emailer.py --recipients recipients.txt
```

### GitHub Actions (single secret)

Create one repository secret named `DAILY_TLDR_ENV` whose value is the full contents of your `.env`, for example:

```
OPENAI_API_KEY=...
GMAIL_USERNAME=you@gmail.com
GMAIL_APP_PASSWORD=abcd abcd abcd abcd
DEFAULT_RECIPIENTS=alice@example.com,bob@example.com
EMAIL_FROM_NAME=Market Daily TL;DR
# Optional
NEWSAPI_KEY=...
SUBJECT_PREFIX=[TL;DR]
```

The workflow at `/.github/workflows/daily-email.yml` writes this secret to `.env` and runs daily at 06:00 UTC.

### macOS scheduling (launchd)

Create a `plist` at `~/Library/LaunchAgents/com.market.dailytldr.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.market.dailytldr</string>
    <key>ProgramArguments</key>
    <array>
      <string>/bin/zsh</string>
      <string>-lc</string>
      <string>cd /Users/divyapersonal/Documents/GitHub/Market-daily-tldr && source .venv/bin/activate && python3 daily_emailer.py --recipients recipients.txt</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
      <key>Hour</key>
      <integer>7</integer>
      <key>Minute</key>
      <integer>30</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/market-dailytldr.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/market-dailytldr.err</string>
    <key>EnvironmentVariables</key>
    <dict>
      <key>PATH</key>
      <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
  </dict>
</plist>
```

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.market.dailytldr.plist
```

### Notes
- Model is hardcoded to `gpt-4o` in `daily_emailer.py`.
- If `NEWSAPI_KEY` is not set, the model will proceed without fresh headlines.
- To test formatting without sending, use `--dry-run`.
- You can also pass recipients inline: `--to alice@example.com,bob@example.com`. 
