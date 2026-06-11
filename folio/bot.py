# Pulse - Daily Summary Bot
# Fetches: weather, a quote, and history
# Actions: Saves summary and emails it securely via Gmail SMTP using GitHub Secrets

import requests
import os
import smtplib
from email.mime.text import MIMEText
from datetime import date

# -- DATA FETCHING FUNCTIONS -------------------------------------------------
def get_weather(city="Thiruvananthapuram"):
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        return f"Weather unavailable ({e})"

def get_quote():
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f'"{data[0]["q"]}" — {data[0]["a"]}'
    except Exception as e:
        return f"Quote unavailable ({e})"

def get_historical_fact():
    url = "https://history.muffinlabs.com/date"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        first_event = data["data"]["Events"][0]
        return f"In {first_event['year']}: {first_event['text']}"
    except Exception as e:
        return f"Historical fact unavailable ({e})"

def build_summary():
    today = date.today().strftime("%A, %d %B %Y")
    return f"""=========================================
PULSE - Daily Summary
{today}
=========================================

WEATHER
{get_weather()}

TODAYS QUOTE
{get_quote()}

THIS DAY IN HISTORY
{get_historical_fact()}

========================================="""

# -- EMAIL AUTOMATION FUNCTION (NEW) ----------------------------------------
def send_email(summary_text):
    """Securely send the summary text to your inbox using environmental secrets."""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    # If secrets aren't configured (like when running locally), skip sending smoothly
    if not sender or not password or not receiver:
        print("Skipping email transmission: GitHub Secrets are not configured locally.")
        return

    msg = MIMEText(summary_text, "plain", "utf-8")
    msg["Subject"] = "Pulse - Your Daily Summary Briefing"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        print("Connecting to Gmail SMTP Server...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Email transmitted successfully! Check your inbox.")
    except Exception as e:
        print(f"Failed to transmit email briefing: {e}")

# -- MAIN EXECUTION ---------------------------------------------------------
def run():
    summary = build_summary()
    print(summary)
    
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
        
    # Send the email!
    send_email(summary)

if __name__ == "__main__":
    run()