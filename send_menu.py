import os
import requests
import time
from menu_scraper import get_weekly_menu

def post_to_discord_webhook():
    """
    Scrapes the weekly menu and posts it to the configured Discord webhook,
    sending each day as a separate, individual message.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("FATAL Error: DISCORD_WEBHOOK_URL environment variable not set.")
        return

    print("Starting weekly menu scrape...")
    # The scraper returns a list of strings, where each string is a formatted menu for one day.
    daily_menus = get_weekly_menu()

    # Check if the scraper returned an error (which will be the only item in the list)
    if len(daily_menus) == 1 and ("error" in daily_menus[0].lower() or "could not find" in daily_menus[0].lower()):
        print(f"Scraping failed or no menu found: {daily_menus[0]}")
        # Optionally send the error to Discord
        # requests.post(webhook_url, json={"content": f"Failed to get menu: {daily_menus[0]}"})
        return

    print(f"Scraping complete. Found {len(daily_menus)} days to post.")

    # --- NEW LOGIC: Loop through each day and send it as a separate message ---
    for i, day_menu_string in enumerate(daily_menus):
        if not day_menu_string.strip():
            continue

        # For the very first message, add a header to the channel.
        content_header = "Here is the menu for the upcoming week!" if i == 0 else None
        
        # --- Create a unique embed for each day ---
        # We will extract the date from the first line of the string to use as the title
        lines = day_menu_string.strip().split('\n')
        # The first line is something like "## 📅 Sunday, June 22", let's clean it up.
        title = lines[0].replace("## 📅", "").strip()
        # The rest of the lines are the description.
        description = "\n".join(lines[1:])

        embed = {
            "title": f"Menu for {title}",
            "description": description,
            "color": 7506394, # A nice blue color
            "footer": {
                "text": "Menu automatically updated"
            }
        }
        
        data = {
            "content": content_header,
            "embeds": [embed]
        }

        print(f"Sending menu for {title}...")
        try:
            response = requests.post(webhook_url, json=data)
            response.raise_for_status() # Raise an exception for bad status codes
            
            # Wait 1 second between each message to avoid Discord rate limits
            if i < len(daily_menus) - 1:
                time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"Error sending message for {title} to webhook: {e}")
            # Stop if one message fails to avoid spamming errors
            break
    else: # This runs if the loop completes without a 'break'
        print("Successfully posted all daily menus to Discord!")


if __name__ == "__main__":
    post_to_discord_webhook()