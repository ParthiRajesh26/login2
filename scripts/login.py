#!/usr/bin/env python3
import os
import sys
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

LOGIN_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
USERNAME_ENV = "LOGIN_USERNAME"
PASSWORD_ENV = "LOGIN_PASSWORD"


def get_credentials():
    username = os.getenv(USERNAME_ENV)
    password = os.getenv(PASSWORD_ENV)
    if not username or not password:
        logging.error(f"Environment variables {USERNAME_ENV} and/or {PASSWORD_ENV} are not set.")
        sys.exit(1)
    return username, password


def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        return driver
    except WebDriverException as e:
        logging.error(f"WebDriver initialization failed: {e}")
        sys.exit(1)


def login(driver, username, password):
    try:
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        user_input = driver.find_element(By.NAME, "username")
        pass_input = driver.find_element(By.NAME, "password")
        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        user_input.clear()
        user_input.send_keys(username)
        pass_input.clear()
        pass_input.send_keys(password)
        login_btn.click()
        # Wait for dashboard or error
        WebDriverWait(driver, 20).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//h6[text()='Dashboard']")),
                EC.presence_of_element_located((By.XPATH, "//p[contains(@class, 'oxd-alert-content-text')]"))
            )
        )
        # Check for successful login
        try:
            driver.find_element(By.XPATH, "//h6[text()='Dashboard']")
            logging.info("Login successful.")
            return True
        except NoSuchElementException:
            logging.error("Login failed: Dashboard not found. Check credentials.")
            return False
    except TimeoutException:
        logging.error("Timeout during login process.")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during login: {e}")
        return False

def main():
    username, password = get_credentials()
    driver = create_driver()
    try:
        success = login(driver, username, password)
        if not success:
            sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
