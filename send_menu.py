import os
import requests
from menu_scraper import get_weekly_menu # This function name is still fine

def post_to_discord_webhook():
    """
    Scrapes the currently available menu and posts it as a single message
    to the configured Discord webhook.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("FATAL Error: DISCORD_WEBHOOK_URL environment variable not set.")
        return

    print("Starting menu scrape...")
    # The scraper returns a single string of the full available menu
    menu_string = get_weekly_menu()

    # Check for errors from the scraper
    if "error" in menu_string.lower() or "could not find" in menu_string.lower():
        print(f"Scraping failed: {menu_string}")
        return

    # Truncate if the message is too long (safety net)
    if len(menu_string) > 4096:
        menu_string = menu_string[:4090] + "\n\n... (message truncated)"

    # Format the message for the webhook
    embed = {
        "title": "Upcoming Foodie.earth Menu",
        "description": menu_string,
        "color": 7506394, # A nice blue color
        "footer": {
            "text": "Menu automatically updated"
        }
    }
    
    data = {
        "content": "Here is the latest available menu!",
        "embeds": [embed]
    }

    print("Sending menu to Discord webhook...")
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending to webhook: {e}")
    else:
        print("Successfully posted menu to Discord!")

if __name__ == "__main__":
    post_to_discord_webhook()
