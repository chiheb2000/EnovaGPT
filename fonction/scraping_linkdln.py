from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import time
import streamlit as st
import pickle

# Initialize WebDriver with options
def get_chrome_driver(headless=False):
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless")  # Run headless Chrome to avoid UI
    options.add_argument("--disable-gpu")  # Disable GPU usage
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chromedriver_path = "C:/Users/chatt/Desktop/Nouveau dossier/Stage enova/Version Final/chromedriver.exe"
    driver = webdriver.Chrome(service=ChromeService(chromedriver_path), options=options)
    return driver

# Function to login to LinkedIn and save cookies
def login_and_save_cookies():
    driver = get_chrome_driver(headless=False)
    driver.get("https://www.linkedin.com/login")
    st.write("Veuillez vous authentifier dans la fenêtre de navigateur ouverte...")
    while True:
        if "feed" in driver.current_url:
            break
        time.sleep(1)
    st.write("Authentification réussie !")
    cookies = driver.get_cookies()
    with open("cookies.pkl", "wb") as file:
        pickle.dump(cookies, file)
    driver.quit() 

# Function to load cookies and reuse the session in a headless browser
def load_cookies_and_get_driver():
    driver = get_chrome_driver(headless=True)
    driver.get("https://www.linkedin.com")
    with open("cookies.pkl", "rb") as file:
        cookies = pickle.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get("https://www.linkedin.com/feed/")
    return driver

# Function to get LinkedIn profiles based on job title
def get_linkedin_profiles(driver, job_title):
    search_url = f'https://www.linkedin.com/search/results/people/?keywords={job_title}&origin=GLOBAL_SEARCH_HEADER'
    driver.get(search_url)
    time.sleep(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    profiles = []
    profile_cards = soup.find_all('li', class_="reusable-search__result-container")
    for profile_card in profile_cards:
        name_tag = profile_card.find('span', class_='entity-result__title-text t-16')
        title_tag = profile_card.find('div', class_='entity-result__primary-subtitle t-14 t-black t-normal')
        link_tag = profile_card.find('a', class_='app-aware-link')
        if name_tag and link_tag:
            aria_hidden_text = name_tag.find('span', {'aria-hidden': 'true'})
            if aria_hidden_text:
                name = aria_hidden_text.get_text(strip=True)
                title = title_tag.get_text(strip=True)
                link = link_tag['href']
                profiles.append({'name': name, 'title': title, 'link': link})

    return profiles



