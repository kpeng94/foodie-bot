# In send_menu.py

import os
import requests
from menu_scraper import get_daily_menu # We reuse the scraper function

def post_to_discord_webhook():
    """
    Scrapes the menu and posts it to the configured Discord webhook.
    """
    # 1. Get the Webhook URL from environment variables
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL environment variable not set.")
        return

    # 2. Scrape the menu data
    # We still use our Selenium scraper from menu_scraper.py
    print("Starting menu scrape...")
    date_string, menu_string, _ = get_daily_menu() # We don't need the raw list here

    # 3. Check for errors from the scraper
    if "error" in date_string.lower() or "could not find" in menu_string.lower():
        print(f"Scraping failed: {menu_string}")
        # Optionally, send an error message to Discord
        # data = {"content": f"Failed to fetch the menu. Reason: {menu_string}"}
        # requests.post(webhook_url, json=data)
        return

    # 4. Format the message for the webhook
    # Discord webhooks expect a specific JSON structure. We'll use an 'embed'.
    embed = {
        "title": f"Weekly Menu for {date_string}",
        "description": menu_string,
        "color": 7506394 # A nice blue color
    }
    
    data = {
        "content": "Here is the menu for the upcoming week!", # Optional main message
        "embeds": [embed]
    }

    # 5. Send the request to the webhook
    print("Sending message to Discord webhook...")
    response = requests.post(webhook_url, json=data)

    if response.status_code >= 400:
        print(f"Error sending to webhook: {response.status_code} {response.text}")
    else:
        print("Successfully posted menu to Discord!")

if __name__ == "__main__":
    post_to_discord_webhook()
