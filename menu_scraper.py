import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_daily_menu():
    """
    Scrapes foodie.earth using Selenium to handle JavaScript loading.
    Returns a tuple: (date_str, menu_str_formatted, list_of_restaurants)
    """
    url = "https://foodie.earth/guest"
    
    # Selenium options to run headless in a Linux environment like GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # The chromedriver will be in the system's PATH in the GitHub Actions runner
    driver = webdriver.Chrome(options=chrome_options)
    
    print("Selenium driver initialized. Navigating to page...")

    try:
        driver.get(url)
        print("Waiting for dynamic content to load...")
        # Wait up to 20 seconds for the menu container to appear
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "current-day")))
        
        print("Content loaded! Parsing HTML with BeautifulSoup...")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        daily_menu_container = soup.find("div", class_="current-day")
        if not daily_menu_container:
            return ("Unknown Date", "Could not find menu container after waiting.", [])

        # --- Date extraction logic ---
        date_str = "Today"
        date_wrapper = daily_menu_container.find("div", class_="day-menu-date-wrapper")
        if date_wrapper:
            date_span = date_wrapper.select_one("span:not([class])")
            if date_span:
                date_str = date_span.get_text(strip=True)

        # --- Menu extraction logic ---
        full_menu_text = []
        available_restaurants_raw = []
        meals_to_find = {"Lunch 🥗": "lunch", "Early Dinner 🌅": "earlyDinner", "Dinner 🌙": "dinner"}

        for meal_name, meal_class in meals_to_find.items():
            meal_section = daily_menu_container.find("div", class_=f"menu-meals {meal_class}")
            if meal_section:
                full_menu_text.append(f"### {meal_name}\n")
                restaurant_containers = meal_section.select("div.meal-list div.meal-menu-container")
                if not restaurant_containers:
                    full_menu_text.append("_No restaurants listed for this meal._\n")
                    continue
                for container in restaurant_containers:
                    restaurant_span = container.find("span", class_="restaurant-name")
                    if restaurant_span:
                        restaurant_name = restaurant_span.get_text(strip=True)
                        if restaurant_name:
                            full_menu_text.append(f"- **{restaurant_name}**\n")
                            available_restaurants_raw.append(restaurant_name)
                if any(f"- **" in s for s in full_menu_text[-len(restaurant_containers):]):
                    full_menu_text.append("\n")

        menu_str_formatted = "".join(full_menu_text)
        if not menu_str_formatted.strip() or not available_restaurants_raw:
             return (date_str, "Menu might not be posted yet.", [])

        return (date_str, menu_str_formatted, available_restaurants_raw)

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return ("Error", f"An error occurred during scraping: {e}", [])
    finally:
        print("Closing Selenium driver.")
        driver.quit()


