import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


USERNAME = os.environ.get("IG_USERNAME", "IG_USERNAME is not set.")
PASSWORD = os.environ.get("IG_PASSWORD", "IG_PASSWORD is not set.")
HOME_URL = "https://instagram.com"


class InstagramCrawler:
    driver: WebDriver
    loggedIn = False

    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("disable-infobars")
        # options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # Chrome is controlled by automated test software
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # avoiding detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(
            executable_path="driver/chromedriver", options=options)

    def auth(self):
        if self.driver is None:
            raise "Driver not initiated."

        self.driver.get(HOME_URL)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username")))

        try:
            self.driver.find_element(
                By.CSS_SELECTOR, "img[data-testid='user-avatar']")
            print("Already logged in.")
            self.loggedIn = True
            return
        except:
            print("Not logged in.")

        print("Logging in using credentials.")

        self.driver.find_element(
            By.NAME, "username").send_keys(USERNAME)
        self.driver.find_element(
            By.NAME, "password").send_keys(PASSWORD)

        self.driver.find_element(
            By.CSS_SELECTOR, "button[type='submit']").click()

        self.loggedIn = True
        # self.set_local_storage()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "img[data-testid='user-avatar']")))

    def set_cookies(self):
        print("Setting cookies")

        # Opening JSON file
        cookieFile = open('./config/igCookies.json')
        cookies = json.load(cookieFile)

        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def set_local_storage(self):
        print("Setting local storage.")

        storageFile = open('config/igLocalStorage.json')
        storageConf = json.load(storageFile)

        for key in storageConf:
            self.driver.execute_script(
                f"localStorage.setItem('{key}', '{storageConf[key]}')")

    def set_session_storage(self):
        print("Setting session storage.")

        storageFile = open('config/igSession.json')
        storageConf = json.load(storageFile)

        for key in storageConf:
            self.driver.execute_script(
                f"sessionStorage.setItem('{key}', '{storageConf[key]}')")

    def upload_video(self):
        if self.loggedIn == False:
            raise "Not logged in"

        self.driver.get(f"{HOME_URL}/aiclippy")

        # WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.TAG_NAME, "main")))

        self.driver.find_element(
            By.CSS_SELECTOR, "[aria-label='New Post']").click()

        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(
            f"{os.getcwd()}/cat.jpg")

        print("Filed added")

        time.sleep(0.5)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Next']")))

        self.driver.find_element(By.XPATH, "//*[text()='Next']").click()

        time.sleep(0.5)

        self.driver.find_element(By.XPATH, "//*[text()='Next']").click()

        time.sleep(0.5)

        self.driver.find_element(By.TAG_NAME, "textarea").send_keys(
            "Cool thing")  # caption
        self.driver.find_element(By.XPATH, "//*[text()='Share']").click()

        print("Uploading...")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Post shared']")))

        print("Uploaded")
