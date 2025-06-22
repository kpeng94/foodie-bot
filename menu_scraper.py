import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException # Import TimeoutException

def get_weekly_menu():
    """
    Scrapes foodie.earth for the entire week's menu using a more robust wait strategy.
    Returns a LIST of strings, where each string is a fully formatted menu for one day.
    """
    url = "https://foodie.earth/guest"
    
    # --- Selenium Setup ---
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    print("Selenium driver initialized...")

    try:
        driver.get(url)
        
        # --- NEW, MORE ROBUST WAIT STRATEGY ---
        print("Waiting for at least 4 'day-menu' divs to load...")
        wait = WebDriverWait(driver, 20) # 20 second timeout
        try:
            # This lambda function tells Selenium to wait until the condition is true:
            # The number of elements found with class 'day-menu' is 4 or more.
            wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, "day-menu")) >= 4)
            print("Found 4 or more daily menus. Proceeding...")
        except TimeoutException:
            # This block runs if the condition isn't met after 20 seconds.
            # This is a graceful fallback in case the site has fewer than 4 days to show.
            print("Warning: Timed out waiting for 4 daily menus. Scraping whatever is available.")
        # --- End of new wait strategy ---

        print("Content loaded! Parsing HTML with BeautifulSoup...")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # The rest of the logic is robust and remains the same.
        main_container = soup.find("div", class_="weekly-menu-content")
        if not main_container:
            return ["Could not find the main 'weekly-menu-content' container."]

        all_days_to_parse = main_container.find_all("div", class_="day-menu")
        if not all_days_to_parse:
            return ["Found main container, but no 'day-menu' divs inside."]

        list_of_daily_menus = []
        print(f"Found {len(all_days_to_parse)} days to parse. Processing now...")
        
        # ... (The rest of the parsing loop remains exactly the same) ...
        for day_element in all_days_to_parse:
            day_parts = []
            date_str = "Unknown Date"
            date_wrapper = day_element.find("div", class_="day-menu-date-wrapper")
            if date_wrapper:
                date_span = date_wrapper.select_one("span:not([class])")
                if date_span:
                    date_str = date_span.get_text(strip=True)
            day_parts.append(f"## 📅 {date_str}\n")
            menu_content = day_element.find("div", class_="menu-content")
            if not menu_content:
                day_parts.append("_No meal information found for this day._\n")
                list_of_daily_menus.append("".join(day_parts))
                continue
            meals_to_find = {"Lunch 🥗": "lunch", "Early Dinner 🌅": "earlyDinner", "Dinner 🌙": "dinner"}
            for meal_name, meal_class in meals_to_find.items():
                meal_section = menu_content.find("div", class_=f"menu-meals {meal_class}")
                if meal_section:
                    day_parts.append(f"### {meal_name}\n")
                    restaurant_containers = meal_section.select("div.meal-list div.meal-menu-container")
                    if not restaurant_containers:
                        day_parts.append("_No restaurants listed for this meal._\n")
                    else:
                        for container in restaurant_containers:
                            restaurant_span = container.find("span", class_="restaurant-name")
                            if restaurant_span and restaurant_span.get_text(strip=True):
                                day_parts.append(f"- **{restaurant_span.get_text(strip=True)}**\n")
                        day_parts.append("\n")
            list_of_daily_menus.append("".join(day_parts))
        return list_of_daily_menus

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return [f"An error occurred during scraping: {e}"]
    finally:
        print("Closing Selenium driver.")
        driver.quit()