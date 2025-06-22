import os
import requests
from menu_scraper import get_weekly_menu

def post_to_discord_webhook():
    """
    Scrapes the weekly menu and posts the next 4 available days
    to the configured Discord webhook.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("FATAL Error: DISCORD_WEBHOOK_URL environment variable not set.")
        return

    print("Starting menu scrape...")
    # The scraper returns a list of strings, one for each day, in chronological order.
    all_daily_menus = get_weekly_menu()

    # Check for errors from the scraper
    if len(all_daily_menus) == 1 and ("error" in all_daily_menus[0].lower() or "could not find" in all_daily_menus[0].lower()):
        print(f"Scraping failed: {all_daily_menus[0]}")
        return

    # Take the first 4 days from the list.
    menus_to_send = all_daily_menus[:4]
    
    if not menus_to_send:
        print("No menus found to send.")
        return

    final_menu_string = "".join(menus_to_send)
    
    # Truncate if the message is too long (safety net)
    if len(final_menu_string) > 4096:
        final_menu_string = final_menu_string[:4090] + "\n\n... (message truncated)"

    # --- MODIFIED: The "footer" section has been removed from the embed below ---
    embed = {
        "title": "Upcoming 4-Day Menu",
        "description": final_menu_string,
        "color": 7506394, # A nice blue color
    }
    
    data = {
        "content": "Here is the latest available menu!",
        "embeds": [embed]
    }

    print(f"Sending {len(menus_to_send)}-day menu to Discord webhook...")
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending to webhook: {e}")
    else:
        print("Successfully posted menu to Discord!")

if __name__ == "__main__":
    post_to_discord_webhook()