import os
import requests
from menu_scraper import get_weekly_menu

def post_to_discord_webhook():
    """
    Scrapes the weekly menu and posts it to the configured Discord webhook.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("FATAL Error: DISCORD_WEBHOOK_URL environment variable not set.")
        return

    print("Starting weekly menu scrape...")
    weekly_menu_string = get_weekly_menu()

    # Check for errors from the scraper
    if "error" in weekly_menu_string.lower() or "could not find" in weekly_menu_string.lower():
        print(f"Scraping failed: {weekly_menu_string}")
        return

    # Discord embed descriptions have a 4096 character limit.
    # We truncate the message if it's too long to prevent an API error.
    if len(weekly_menu_string) > 4096:
        weekly_menu_string = weekly_menu_string[:4090] + "\n\n... (message truncated)"

    # Format the message for the webhook
    embed = {
        "title": "Upcoming Weekly Menu",
        "description": weekly_menu_string,
        "color": 7506394, # A nice blue color
        "footer": {
            "text": "Menu automatically updated"
        }
    }
    
    data = {
        "content": "Here is the menu for the upcoming week!",
        "embeds": [embed]
    }

    print("Sending message to Discord webhook...")
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending to webhook: {e}")
    else:
        print("Successfully posted weekly menu to Discord!")

if __name__ == "__main__":
    post_to_discord_webhook()

