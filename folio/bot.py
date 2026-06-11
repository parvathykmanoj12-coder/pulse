# Pulse - Daily Summary Bot with OpenWeatherMap Alerts
import requests
import os
import smtplib
from email.mime.text import MIMEText
from datetime import date

# -- FUNCTION 1: OpenWeatherMap API Fetcher & Alert Evaluator -----------------
def check_weather_alerts(city="Thiruvananthapuram"):
    """Fetches data from OpenWeatherMap and checks for severe heat (>35C) or rain."""
    api_key = os.environ.get("WEATHER_API_KEY")
    
    if not api_key:
        return False, "OpenWeatherMap API Key missing from environment.", "Could not evaluate alerts."
        
    # URL configured for metric units (Celsius)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current_temp = data["main"]["temp"]
        weather_conditions = data["weather"]
        
        # Extract clear textual descriptions (e.g., 'broken clouds', 'light rain')
        descriptions = [condition["description"] for condition in weather_conditions]
        condition_summary = ", ".join(descriptions)
        
        report = f"Current Temperature in {city}: {current_temp}°C | Conditions: {condition_summary.capitalize()}"
        
        alert_triggered = False
        alert_reasons = []
        
        # 1. Check Temperature Condition (> 35°C)
        if current_temp > 35:
            alert_triggered = True
            alert_reasons.append(f"⚠️ EXTREME HEAT ALERT: Current temperature is {current_temp}°C (Exceeds 35°C limit!)")
            
        # 2. Check Rain Condition (If 'rain' appears in any weather condition keywords)
        is_raining = any("rain" in desc.lower() or "drizzle" in desc.lower() for desc in descriptions)
        if is_raining:
            alert_triggered = True
            alert_reasons.append(f"临 RAIN ALERT DETECTED: Previews indicate atmospheric precipitation is falling right now!")
            
        alert_message = "\n".join(alert_reasons) if alert_triggered else "✅ Weather conditions are normal."
        return alert_triggered, report, alert_message

    except Exception as e:
        return False, f"OpenWeatherMap tracking offline ({e})", "Could not safely gauge alerts."

# -- FUNCTION 2: Quote -------------------------------------------------------
def get_quote():
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f'"{data[0]["q"]}" — {data[0]["a"]}'
    except Exception as e:
        return f"Quote unavailable ({e})"

# -- FUNCTION 3: History -----------------------------------------------------
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

# -- FUNCTION 4: Email Dispatches --------------------------------------------
def send_email(subject, body_text):
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    if not sender or not password or not receiver:
        print("Skipping email transmission: Email secrets are not configured locally.")
        return

    msg = MIMEText(body_text, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        print(f"Connecting to SMTP to forward briefing: '{subject}'...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("Email transmitted successfully!")
    except Exception as e:
        print(f"Failed to transmit email package: {e}")

# -- MAIN ENGINE RUNNER ------------------------------------------------------
def run():
    today = date.today().strftime("%A, %d %B %Y")
    
    alert_triggered, weather_report, alert_message = check_weather_alerts()
    quote = get_quote()
    history = get_historical_fact()
    
    summary = f"""=========================================
PULSE - Daily Summary Briefing
{today}
=========================================

WEATHER (OPENWEATHERMAP)
{weather_report}

ALERT EVALUATION STATUS
{alert_message}

TODAYS MOTIVATIONAL QUOTE
{quote}

THIS DAY IN HISTORY
{history}

========================================="""

    print(summary)
    
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    # Change subject dynamically based on evaluation metrics
    if alert_triggered:
        subject = "🚨 PULSE CRITICAL WEATHER ALERT: Verification Required!"
    else:
        subject = "Pulse - Your Daily Summary Briefing"

    send_email(subject, summary)

if __name__ == "__main__":
    run()