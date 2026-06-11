# Pulse - Daily Summary Bot
# Fetches: weather (wttr.in), a quote (zenquotes.io), and history (history.muffinlabs.com)
# Runs:    every day at 8 AM IST via GitHub Actions

import requests
from datetime import date

# -- FUNCTION 1: Weather -----------------------------------------------------
def get_weather(city="Thiruvananthapuram"):
    """Fetch today's weather as a one-line text summary."""
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        return f"Weather unavailable ({e})"

# -- FUNCTION 2: Quote -------------------------------------------------------
def get_quote():
    """Fetch a random motivational quote from ZenQuotes."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        return f'"{quote}" — {author}'
    except Exception as e:
        return f"Quote unavailable ({e})"

# -- FUNCTION 3: This Day in History (NEW) -----------------------------------
def get_historical_fact():
    """Fetch a significant historical event that happened on this day."""
    url = "https://history.muffinlabs.com/date"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Grab the very first event from the list for today
        first_event = data["data"]["Events"][0]
        year = first_event["year"]
        text = first_event["text"]
        return f"In {year}: {text}"
    except Exception as e:
        return f"Historical fact unavailable ({e})"

# -- FUNCTION 4: Build the summary ------------------------------------------
def build_summary():
    """Assemble the full daily summary from all data sources."""
    today = date.today().strftime("%A, %d %B %Y")
    weather = get_weather()
    quote = get_quote()
    history = get_historical_fact()
    
    summary = f"""=========================================
PULSE - Daily Summary
{today}
=========================================

WEATHER
{weather}

TODAYS QUOTE
{quote}

THIS DAY IN HISTORY
{history}

========================================="""
    return summary

# -- FUNCTION 5: Run everything ---------------------------------------------
def run():
    """Main entry point. Called by GitHub Actions."""
    summary = build_summary()
    
    # Print to the GitHub Actions log
    print(summary)
    
    # Save to a file (uploaded as an artifact)
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
        
    print("Pulse ran successfully.")

if __name__ == "__main__":
    run()