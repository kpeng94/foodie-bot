import os
import requests
import time
from menu_scraper import get_weekly_menu

def post_to_discord_webhook():
    """
    Scrapes the weekly menu and posts it to the configured Discord webhook,
    intelligently grouping days into messages to respect character limits.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("FATAL Error: DISCORD_WEBHOOK_URL environment variable not set.")
        return

    print("Starting weekly menu scrape...")
    # Scraper now returns a list of strings, one for each day.
    daily_menus = get_weekly_menu()

    # Check for errors from the scraper (which will be the only item in the list)
    if len(daily_menus) == 1 and ("error" in daily_menus[0].lower() or "could not find" in daily_menus[0].lower()):
        print(f"Scraping failed: {daily_menus[0]}")
        return

    # --- NEW, ROBUST CHUNKING LOGIC ---
    # This logic combines full day-menus into chunks.
    limit = 4000
    message_chunks = []
    current_chunk = ""

    for day_menu in daily_menus:
        # If adding the next full day menu exceeds the limit...
        if len(current_chunk) + len(day_menu) > limit:
            # ...and the current chunk is not empty, save it.
            if current_chunk:
                message_chunks.append(current_chunk)
            # Start the new chunk with the current day's menu.
            current_chunk = day_menu
        else:
            # Otherwise, add the next day's menu to the current chunk.
            current_chunk += day_menu
    
    # Add the final chunk to the list after the loop finishes.
    if current_chunk:
        message_chunks.append(current_chunk)
    # --- End of new chunking logic ---

    if not message_chunks:
        print("No content to send after processing.")
        return
        
    print(f"Menu has been split into {len(message_chunks)} messages.")

    # Sending loop remains the same
    for i, chunk in enumerate(message_chunks):
        content_header = "Here is the menu for the upcoming week!" if i == 0 else None
        
        embed_title = "Upcoming Weekly Menu"
        if len(message_chunks) > 1:
            embed_title += f" (Part {i+1}/{len(message_chunks)})"

        embed = {
            "title": embed_title,
            "description": chunk,
            "color": 7506394, # A nice blue color
            "footer": {
                "text": "Menu automatically updated"
            }
        }
        
        data = {
            "content": content_header,
            "embeds": [embed]
        }

        print(f"Sending chunk {i+1} of {len(message_chunks)} to Discord webhook...")
        try:
            response = requests.post(webhook_url, json=data)
            response.raise_for_status()
            
            if i < len(message_chunks) - 1:
                time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"Error sending chunk {i+1} to webhook: {e}")
            break
    else:
        print("Successfully posted all menu chunks to Discord!")


if __name__ == "__main__":
    post_to_discord_webhook()