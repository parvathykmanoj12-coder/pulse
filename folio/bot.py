# Pulse - Advanced News Scraper & Dynamic HTML Mailer
import requests
import os
import smtplib
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# -- DATA FETCHING FUNCTIONS -------------------------------------------------
def get_weather(city="Thiruvananthapuram"):
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return "Weather API Key missing."
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f"{data['main']['temp']}°C, {data['weather'][0]['description'].capitalize()}"
    except Exception as e:
        return f"Weather metrics unavailable ({e})"

def get_quote():
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f'"{data[0]["q"]}" — {data[0]["a"]}'
    except:
        return "Keep pushing forward no matter what."

# -- TASK 2: MULTI-SOURCE HEADLINE WEB SCRAPER -------------------------------
def scrape_news_headlines():
    """Scrapes top headlines dynamically from 3 independent sources."""
    headlines = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # Source 1: BBC News
    try:
        res = requests.get("https://www.bbc.com/news", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # BBC uses h2 tags for prime headlines
        title = soup.find('h2').get_text(strip=True)
        headlines.append({"source": "BBC News", "title": title, "url": "https://www.bbc.com/news"})
    except Exception as e:
        headlines.append({"source": "BBC News", "title": "Failed to scrape latest headlines", "url": "#"})

    # Source 2: Hacker News (Tech headlines)
    try:
        res = requests.get("https://news.ycombinator.com/", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        story = soup.find('span', class_='titleline').find('a')
        headlines.append({"source": "Hacker News", "title": story.get_text(strip=True), "url": story['href']})
    except Exception as e:
        headlines.append({"source": "Hacker News", "title": "Failed to scrape tech logs", "url": "#"})

    # Source 3: Times of India / Alternative RSS/News endpoint
    try:
        res = requests.get("https://news.google.com/news/rss", headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'xml') # parse standard XML structure
        item = soup.find('item')
        headlines.append({"source": "Google News Global", "title": item.title.text, "url": item.link.text})
    except Exception as e:
        headlines.append({"source": "Google News", "title": "Failed to extract international briefing", "url": "#"})

    return headlines

# -- BUILDING THE FORMATTED HTML NEWSLETTER TEMPLATE -------------------------
def build_html_summary(weather, quote, news_list):
    time_stamp = datetime.now().strftime("%I:%M %p | %A, %d %B %Y")
    
    # Generate dynamic list items for news loop
    news_html_blocks = ""
    for item in news_list:
        news_html_blocks += f"""
        <div style="margin-bottom: 15px; padding-left: 10px; border-left: 4px solid #4A90E2;">
            <strong style="color: #4A90E2; font-size: 12px; text-transform: uppercase;">{item['source']}</strong><br/>
            <a href="{item['url']}" style="color: #333; text-decoration: none; font-size: 16px; font-weight: bold;">{item['title']}</a>
        </div>
        """

    # Combined clean responsive HTML grid wrap
    html_layout = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; padding: 20px; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <h2 style="color: #2C3E50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; margin-top: 0;">📊 PULSE - Daily Intelligence Briefing</h2>
            <p style="color: #7F8C8D; font-size: 13px;">Compiled at: {time_stamp}</p>
            
            <div style="background: #EBF5FB; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                <h4 style="margin: 0 0 5px 0; color: #2980B9;">🌤️ Real-Time Weather Report</h4>
                <p style="margin: 0; font-size: 15px; color: #34495E;">{weather}</p>
            </div>

            <div style="margin-bottom: 25px;">
                <h4 style="margin: 0 0 10px 0; color: #2C3E50; text-transform: uppercase; font-size: 13px; letter-spacing: 1px;">📰 Top Headings Scraping Log</h4>
                {news_html_blocks}
            </div>

            <div style="background: #FFF9E6; padding: 15px; border-radius: 6px; border-left: 4px solid #F1C40F;">
                <h5 style="margin: 0 0 5px 0; color: #B7950B; text-transform: uppercase;">💭 Thought of the Day</h5>
                <p style="margin: 0; font-style: italic; color: #7D6608; font-size: 14px;">{quote}</p>
            </div>
            
            <p style="text-align: center; font-size: 11px; color: #BDC3C7; margin-top: 30px;">Pulse Engine Pipeline • Powered autonomously by GitHub Actions</p>
        </div>
    </body>
    </html>
    """
    return html_layout

# -- EMAIL AUTOMATION DISPATCH ENGINE -----------------------------------------
def send_html_email(html_body):
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    if not sender or not password or not receiver:
        print("Skipping pipeline execution: Local settings sandbox.")
        return

    # Use MIMEMultipart structure to indicate this is a styled HTML payload instead of text
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "☕ Pulse - Your Morning HTML Newsletter"
    msg["From"] = sender
    msg["To"] = receiver
    
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        print("Connecting to secure SMTP node to stream newsletter payload...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("HTML Briefing compiled and forwarded successfully!")
    except Exception as e:
        print(f"Failed to complete SMTP payload delivery: {e}")

# -- MAIN ENGINES RUNNER -----------------------------------------------------
def run():
    weather = get_weather()
    quote = get_quote()
    news = scrape_news_headlines()
    
    html_content = build_html_summary(weather, quote, news)
    
    # Save text/html log locally
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    send_html_email(html_content)

if __name__ == "__main__":
    run()