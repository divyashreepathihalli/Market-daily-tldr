from __future__ import annotations

import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import List
import re

from dotenv import load_dotenv
from openai import OpenAI

from email_providers import send_email
from templates import PROMPT_TEMPLATE, SYSTEM_INSTRUCTIONS, build_email_subject

MODEL_NAME = "gpt-4o"


def get_model_name() -> str:
    return os.getenv("OPENAI_MODEL_OVERRIDE", MODEL_NAME)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Market Daily TL;DR emailer")
    parser.add_argument("--to", help="Comma-separated email addresses", default=None)
    parser.add_argument("--recipients", help="Path to file with one email per line", default=None)
    parser.add_argument("--no-news", action="store_true", help="(unused) kept for compatibility")
    parser.add_argument("--subject-prefix", help="Optional subject prefix", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Print output instead of sending email")
    return parser.parse_args()


def load_recipients(args: argparse.Namespace) -> List[str]:
    candidates: List[str] = []

    if args.to:
        candidates.extend([addr.strip() for addr in args.to.split(",") if addr.strip()])

    if args.recipients:
        path = Path(args.recipients)
        if not path.exists():
            raise SystemExit(f"Recipients file not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    candidates.append(line)

    if not candidates:
        env_default = os.getenv("DEFAULT_RECIPIENTS", "").strip()
        if env_default:
            candidates.extend([addr.strip() for addr in env_default.split(",") if addr.strip()])

    unique = sorted(set(candidates))
    if not unique:
        raise SystemExit("No recipients provided. Use --to, --recipients, or DEFAULT_RECIPIENTS in env.")
    return unique


def call_openai(news_context: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    prompt = PROMPT_TEMPLATE.format(news_context=news_context or "")

    completion = client.chat.completions.create(
        model=get_model_name(),
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1200,
    )

    content = completion.choices[0].message.content or ""
    if not content.strip():
        raise SystemExit("Model returned empty content; aborting send.")
    return content


def main() -> None:
    load_dotenv(override=False)

    args = parse_args()
    recipients = load_recipients(args)

    subject_prefix = args.subject_prefix or os.getenv("SUBJECT_PREFIX", "").strip() or None
    subject = build_email_subject(subject_prefix)

    # Send LLM output as-is (no additional wrapping/validation)
    body = call_openai(news_context="")

    if args.dry_run:
        print(f"SUBJECT: {subject}")
        print("RECIPIENTS:", ", ".join(recipients))
        print(body)
        return

    from_address = os.getenv("EMAIL_FROM_ADDRESS") or os.getenv("GMAIL_USERNAME")
    if not from_address:
        raise SystemExit("EMAIL_FROM_ADDRESS or GMAIL_USERNAME must be set for sender address")

    from_name = os.getenv("EMAIL_FROM_NAME", "Market Daily TL;DR")

    send_email(
        subject=subject,
        html_body=body,
        recipients=recipients,
        from_address=from_address,
        from_name=from_name,
    )

    print(f"Sent {len(recipients)} emails: {', '.join(recipients)}")


if __name__ == "__main__":
    main() 