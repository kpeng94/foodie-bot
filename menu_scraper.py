import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_weekly_menu():
    """
    Scrapes foodie.earth for the entire week's menu.
    Returns a single, formatted string containing the menu for all available days.
    """
    url = "https://foodie.earth/guest"
    
    # Selenium options to run headless in a Linux environment like GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    print("Selenium driver initialized. Navigating to page...")

    try:
        driver.get(url)
        print("Waiting for dynamic content to load...")
        wait = WebDriverWait(driver, 20)
        
        # --- MODIFIED LINE ---
        # Wait for the correct top-level container to appear.
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "weekly-menu-content")))
        
        print("Content loaded! Parsing HTML with BeautifulSoup...")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # The rest of the parsing logic remains the same, as it looks for elements
        # within the main container which has now been correctly identified.
        all_days_to_parse = []
        current_day_element = soup.find("div", class_="current-day")
        if current_day_element:
            all_days_to_parse.append(current_day_element)

        upcoming_days_container = soup.find("div", class_="upcoming-days")
        if upcoming_days_container:
            upcoming_day_elements = upcoming_days_container.find_all("div", class_="day-menu")
            all_days_to_parse.extend(upcoming_day_elements)
        
        if not all_days_to_parse:
            return "Could not find any daily menu information on the page."

        weekly_menu_parts = []
        for day_element in all_days_to_parse:
            date_str = "Unknown Date"
            date_wrapper = day_element.find("div", class_="day-menu-date-wrapper")
            if date_wrapper:
                date_span = date_wrapper.select_one("span:not([class])")
                if date_span:
                    date_str = date_span.get_text(strip=True)
            
            weekly_menu_parts.append(f"\n## 📅 {date_str}\n")

            menu_content = day_element.find("div", class_="menu-content")
            if not menu_content:
                weekly_menu_parts.append("_No meal information found for this day._\n")
                continue

            meals_to_find = {"Lunch 🥗": "lunch", "Early Dinner 🌅": "earlyDinner", "Dinner 🌙": "dinner"}
            for meal_name, meal_class in meals_to_find.items():
                meal_section = menu_content.find("div", class_=f"menu-meals {meal_class}")
                if meal_section:
                    weekly_menu_parts.append(f"### {meal_name}\n")
                    restaurant_containers = meal_section.select("div.meal-list div.meal-menu-container")
                    if not restaurant_containers:
                        weekly_menu_parts.append("_No restaurants listed for this meal._\n")
                    else:
                        for container in restaurant_containers:
                            restaurant_span = container.find("span", class_="restaurant-name")
                            if restaurant_span and restaurant_span.get_text(strip=True):
                                weekly_menu_parts.append(f"- **{restaurant_span.get_text(strip=True)}**\n")
                        weekly_menu_parts.append("\n")

        return "".join(weekly_menu_parts)

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return f"An error occurred during scraping: {e}"
    finally:
        print("Closing Selenium driver.")
        driver.quit()
