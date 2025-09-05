import json
"""
API logic redacted for demo purposes.
"""
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import whois

def whois_creation_date(domain_name):
    w = whois.whois(domain_name)
    creation_date = w.creation_date
    if isinstance(creation_date, list):
        creation_date = creation_date[0]
    return int(creation_date.year)

def get_registered_domains(tld):
    """Fetches the number of registered domains using headless Selenium and JavaScript execution."""

    with open('tld_dict.json') as f:
        id_dict = json.load(f)

    # Reverse the keys and values so that the TLDs are the keys
    id_dict = {v: k for k, v in id_dict.items()}

    id = id_dict[tld]

    # url redacted for demo purposes
    url = "[REDACTED_FOR_DEMO]"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode
   # options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    time.sleep(5)  # Wait for 5 seconds after loading the page

    try:
        # Wait for the element to be present and loaded
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tld-domains-count"))
        )
        return element.text
    except TimeoutException:
        return None
    finally:
        driver.quit()

def get_domain_price(exact_domain):
    # Construct the URL
    # url redacted for demo purposes
    url = "[REDACTED_FOR_DEMO]"

    # Set up Headless Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)

        # Wait for the page to load
        driver.implicitly_wait(10)

        # Get the page source
        page_source = driver.page_source

        # Use regular expressions to find the exact domain and its price
        match = re.search(f'name="{exact_domain}".*?</tr>', page_source, re.DOTALL)

        if match:
            domain_area = match.group()

            # Find the price (as before)
            price_match = re.search(r'\$ ?\d{1,3}(?:,\d{3})*\.\d{2}\s+USD', domain_area)

            # Find the date 
            date_match = re.search(r'(?:<a href="/stats/stats-by-year/\?sy=)(\d{4})(?:&amp;.*>)', domain_area)

            if price_match and date_match: 
                price = price_match.group()
                date = date_match.group(1)  # Extract the year
                return exact_domain, price, date
            else:
                return None, "Price or date not found" 
        else:
            return None, "Domain not found"

    except Exception as e:
        return None, f"An error occurred: {e}"

    finally:
        driver.quit()

if __name__ == "__main__":
    # Get the number of registered domains
    tld = "us"
    number_of_domains = get_registered_domains(tld)

    if number_of_domains:
        print(f"Number of registered domains: {number_of_domains}")
    else:
        print("Could not find the number of registered domains.")