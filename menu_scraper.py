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
    Scrapes foodie.earth for the entire week's menu using a simplified and robust logic.
    Returns a LIST of strings, where each string is a fully formatted menu for one day.
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
    print("Selenium driver initialized...")

    try:
        driver.get(url)
        print("Waiting for dynamic content to load...")
        wait = WebDriverWait(driver, 20)
        # Wait for the correct top-level container to appear
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "weekly-menu-content")))
        
        print("Content loaded! Parsing HTML with BeautifulSoup...")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Find the single main container that holds all the days
        main_container = soup.find("div", class_="weekly-menu-content")
        if not main_container:
            return ["Could not find the main 'weekly-menu-content' container."]

        # Find ALL 'day-menu' divs directly within the main container
        all_days_to_parse = main_container.find_all("div", class_="day-menu")
        
        if not all_days_to_parse:
            return ["Found main container, but no 'day-menu' divs inside."]

        # Build a list of day strings
        list_of_daily_menus = []
        print(f"Found {len(all_days_to_parse)} days to parse...")
        
        for day_element in all_days_to_parse:
            day_parts = []
            
            # Get the date for the current day block
            date_str = "Unknown Date"
            date_wrapper = day_element.find("div", class_="day-menu-date-wrapper")
            if date_wrapper:
                date_span = date_wrapper.select_one("span:not([class])")
                if date_span:
                    date_str = date_span.get_text(strip=True)
            
            day_parts.append(f"## 📅 {date_str}\n")

            # Get the meals for the current day block
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
            
            # Add the completed string for this day to the main list
            list_of_daily_menus.append("".join(day_parts))

        return list_of_daily_menus

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return [f"An error occurred during scraping: {e}"]
    finally:
        print("Closing Selenium driver.")
        driver.quit()