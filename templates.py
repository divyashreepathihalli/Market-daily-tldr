from __future__ import annotations
from datetime import datetime

PROMPT_USA_BODY = (
    "You are a financial research assistant. Summarize today’s most important news across the following categories, focusing only on information that could influence stock market decisions:\n\n"
    "Political News – Include global and U.S. political developments, elections, new legislation, regulatory actions, and geopolitical tensions that could impact markets.\n\n"
    "World News – Cover major events such as conflicts, treaties, economic crises, trade agreements, natural disasters, and significant policy changes in other countries.\n\n"
    "U.S. News – Include domestic economic data releases, Fed announcements, inflation reports, consumer sentiment, unemployment data, and major policy changes.\n\n"
    "Technology News – Summarize breakthroughs, product launches, mergers/acquisitions, cybersecurity incidents, AI developments, and semiconductor industry updates.\n\n"
    "Trending Infrastructure & Energy News – Include large-scale construction projects, renewable energy investments, oil & gas developments, transportation initiatives, and related government contracts.\n\n"
    "Market-Relevant Trends – Highlight emerging consumer behavior shifts, new market opportunities, or major corporate earnings that could influence sectors.\n\n"
    "For each category, provide:\n\n"
    "Headline (short and clear)\n\n"
    "1–3 sentence summary\n\n"
    "Potential market impact (Bullish, Bearish, Neutral) with reasoning\n\n"
    "End with a brief overall sentiment summary (Bullish/Bearish/Neutral) and list 3–5 sectors or tickers that might be most affected today."
)

PROMPT_INDIA_BODY = (
    "You are a financial research assistant. Summarize today’s most important India-focused news across the following categories, focusing only on information that could influence stock market decisions:\n\n"
    "Political News (India) – Include national political developments, new bills or amendments, policy changes, trade negotiations, election updates, and geopolitical tensions involving India.\n\n"
    "World News Relevant to India – Summarize major global events such as oil price changes, foreign investment policies, trade agreements, sanctions, global economic shifts, and geopolitical developments that could impact Indian markets.\n\n"
    "Indian Economy & Domestic News – Cover RBI announcements, monetary policy updates, GDP growth figures, inflation rates, unemployment data, industrial production, foreign exchange reserves, and major government initiatives.\n\n"
    "Technology & Startup News (India) – Include IPOs, mergers & acquisitions, funding rounds, government tech policies, AI and semiconductor initiatives, and cybersecurity incidents relevant to Indian tech firms.\n\n"
    "Infrastructure, Energy & Manufacturing News – Summarize developments in renewable energy, oil & gas, transport infrastructure, large public-private partnership projects, real estate, and manufacturing sector trends.\n\n"
    "Sector-Specific Corporate News – Highlight major earnings, expansion plans, regulatory approvals, or product launches by companies listed on NSE/BSE.\n\n"
    "For each category, provide:\n\n"
    "Headline (short and clear)\n\n"
    "1–3 sentence summary\n\n"
    "Potential market impact (Bullish, Bearish, Neutral) with reasoning\n\n"
    "End with:\n\n"
    "Overall market sentiment (Bullish/Bearish/Neutral)\n\n"
    "Top 3–5 sectors or specific NSE/BSE tickers likely to be most affected today"
)

SYSTEM_INSTRUCTIONS_BASE = (
    "You are a precise financial research assistant. If no external context is provided, use your internal knowledge to provide concrete, non-placeholder insights for every category.\n"
    "Do not wrap the response in Markdown or code fences of any kind. Output direct HTML only.\n"
    "Produce clean, email-ready HTML with <h2>/<h3>/<p>/<ul>/<li> tags, no external CSS."
)

SYSTEM_INSTRUCTIONS_USA = (
    SYSTEM_INSTRUCTIONS_BASE
    + "\nCenter ALL sections on the United States market: S&P 500, Dow, Nasdaq, major US sectors, USD, UST yields, Fed/FOMC, CPI/PCE, SEC/FTC/DOJ, and major US companies/tickers."
)

SYSTEM_INSTRUCTIONS_INDIA = (
    SYSTEM_INSTRUCTIONS_BASE
    + "\nCenter ALL sections on India: NIFTY 50, NIFTY BANK, NSE/BSE sectors, INR, G-Sec yields, RBI/MPC, CPI/WPI, SEBI/MCA/GST, and major Indian companies/tickers."
)

PROMPT_TEMPLATE = (
    "<context>\n" 
    "{news_context}\n"
    "</context>\n\n"
    "<task>\n"
    "{prompt_body}\n"
    "Output strictly as HTML with clear sections per category and an overall sentiment section at the end.\n"
    "</task>\n"
)


def build_email_subject(subject_prefix: str | None = None) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    base = f"Market Daily TL;DR — {today}"
    if subject_prefix:
        return f"{subject_prefix} {base}"
    return base


def get_system_instructions(focus_market: str | None) -> str:
    if not focus_market:
        return SYSTEM_INSTRUCTIONS_BASE
    fm = focus_market.lower()
    if "india" in fm:
        return SYSTEM_INSTRUCTIONS_INDIA
    if "united states" in fm or "u.s." in fm or "usa" in fm or "us" == fm or fm.endswith(" us"):
        return SYSTEM_INSTRUCTIONS_USA
    return SYSTEM_INSTRUCTIONS_BASE


def build_user_prompt(news_context: str, focus_market: str | None) -> str:
    fm = (focus_market or "").lower()
    if "india" in fm:
        body = PROMPT_INDIA_BODY
    else:
        body = PROMPT_USA_BODY
    return PROMPT_TEMPLATE.format(news_context=news_context or "", prompt_body=body)


EMAIL_HTML_SHELL = """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{subject}</title>
  </head>
  <body style=\"font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#111; line-height:1.5; margin:0; padding:0; background:#f7f7f7;\">
    <div style=\"max-width:720px; margin:0 auto; padding:24px;\">
      <div style=\"background:#ffffff; border-radius:10px; padding:24px; box-shadow:0 1px 3px rgba(0,0,0,0.06);\">
        <h1 style=\"margin:0 0 12px; font-size:20px;\">{subject}</h1>
        <div style=\"font-size:14px; color:#666; margin-bottom:16px;\">Generated {generated_at}</div>
        <div>{content_html}</div>
        <hr style=\"border:none; border-top:1px solid #eee; margin:24px 0;\" />
        <div style=\"font-size:12px; color:#888;\">
          You are receiving this email because you subscribed to Market Daily TL;DR.\n
        </div>
      </div>
    </div>
  </body>
</html>
""" 