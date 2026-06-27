# CS2 Update Notifier

An automated, serverless application that monitors the Counter-Strike 2 update feed and sends a formatted email notification whenever Valve releases a patch. 

## How It Works

The full pipeline runs on a schedule every 30 minutes:

1. **Trigger** — AWS EventBridge fires the Lambda function on a cron schedule.
2. **Fetch** — The function fetches the CS2 RSS feed (XML) using Python's `urllib` and parses it with `xml.etree.ElementTree` to extract the latest update's title, date, GUID, and raw HTML description.
3. **Dedup check** — The GUID of the latest update is compared against the last-seen GUID stored in a DynamoDB table (`CS2-update-tracker`). If they match, execution stops — no duplicate emails.
4. **Parse** — If the update is new, a custom `HTMLParser` subclass (`UpdateParser`) converts the raw HTML patch notes into clean, readable plain text, turning `<li>` elements into bullet points and preserving section headers.
5. **Email** — The formatted patch notes are sent as a plain-text email via AWS SES (Gmail SMTP locally) with the subject line `CS2 Update - <date>`.
6. **Save** — The new GUID is written back to DynamoDB so future runs know this update has already been processed.

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12 |
| Compute | AWS Lambda |
| Scheduler | AWS EventBridge (every 30 minutes) |
| State | AWS DynamoDB |
| Email (prod) | AWS SES |
| Email (local) | Gmail SMTP |
| Feed source | XML RSS via `urllib` + `xml.etree.ElementTree` |
| HTML parsing | Custom `HTMLParser` subclass |

## Local Setup

**Prerequisites:** Python 3.12, pip, AWS credentials configured locally (for DynamoDB access)

**1. Clone the repository**
```bash
git clone https://github.com/TrevorMcCormack/CS2-Update-Notifier.git
cd "CS2-Update-Notifier"
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create a `.env` file** in the project root with your Gmail credentials:
```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
```

> You'll need a [Gmail App Password](https://support.google.com/accounts/answer/185833), not your regular account password.

**4. Run locally**
```bash
python main.py
```

The script will check the RSS feed, compare against DynamoDB, and send an email if a new update is found.

## Project Status

**Fully deployed and running.** The Lambda function is live on AWS, triggered automatically by EventBridge every 30 minutes. DynamoDB persists state between invocations to guarantee exactly-once delivery per update.
