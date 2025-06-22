import os
import requests
import time
from menu_scraper import get_weekly_menu

def post_to_discord_webhook():
    """
    Scrapes the weekly menu and posts it to the configured Discord webhook,
    splitting it into multiple messages if it exceeds the character limit.
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

    # --- NEW: Logic to split the message into chunks ---
    # Discord's embed description limit is 4096. We'll use a safer limit.
    limit = 4000
    
    # Split the menu string into individual lines
    lines = weekly_menu_string.split('\n')
    
    # Group lines into chunks that fit within the limit
    message_chunks = []
    current_chunk = ""
    for line in lines:
        if len(current_chunk) + len(line) + 1 > limit:
            message_chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line + "\n"
    
    # Add the last chunk to the list
    if current_chunk:
        message_chunks.append(current_chunk)
    # --- End of splitting logic ---

    print(f"Menu has been split into {len(message_chunks)} messages.")

    # Send each chunk as a separate message
    for i, chunk in enumerate(message_chunks):
        # For the first message, add a "content" header.
        content_header = "Here is the menu for the upcoming week!" if i == 0 else None
        
        # Adjust the title for subsequent parts
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

        print(f"Sending chunk {i+1} to Discord webhook...")
        try:
            response = requests.post(webhook_url, json=data)
            response.raise_for_status() # Raise an exception for bad status codes
            
            # Wait 1 second between messages to avoid Discord rate limits
            if i < len(message_chunks) - 1:
                time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"Error sending chunk {i+1} to webhook: {e}")
            # Stop if one chunk fails
            break
    else: # This 'else' belongs to the 'for' loop, it runs if the loop completes without a 'break'
        print("Successfully posted all menu chunks to Discord!")


if __name__ == "__main__":
    post_to_discord_webhook()
