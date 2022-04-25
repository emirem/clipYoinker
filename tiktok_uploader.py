import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement


USERNAME = "aiclippy"
PASSWORD = "LJrQbiU3Z9x6"
HOME_URL = "https://m.tiktok.com"


class TikTokCrawler:
    driver: WebDriver

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
        options.add_argument("--profile-directory=Default")
        options.add_argument(
            "--user-data-dir=C:/Users/Admin/AppData/Local/Google/Chrome/User Data")

        # avoiding detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(
            executable_path="driver/chromedriver", options=options)

    def auth(self):
        if self.driver is None:
            raise "Driver not initiated."

        self.driver.get(HOME_URL)
        self.set_cookies()
        # self.set_local_storage()
        # self.set_session_storage()

        # There's captcha, so need to figure out way around
        # self.driver.get(HOME_URL)

        # self.driver.find_element(
        #     By.CSS_SELECTOR, "button[data-e2e='top-login-button']").click()

        # loginBtn = self.driver.find_element(
        #     By.CSS_SELECTOR, "div[class*='channel-item-wrapper-']")

        # print(loginBtn)

    def set_cookies(self):
        print("Setting cookies")

        # Opening JSON file
        cookieFile = open('cookies.json')
        cookies = json.load(cookieFile)

        for cookie in cookies:
            print(cookie)
            self.driver.add_cookie(cookie)

    def set_local_storage(self):
        print("Setting local storage.")

        storageFile = open('localStorage.json')
        storageConf = json.load(storageFile)

        for key in storageConf:
            print("line", key)
            self.driver.execute_script(
                f"localStorage.setItem('{key}', '{storageConf[key]}')")

    def set_session_storage(self):
        print("Setting session storage.")

        storageFile = open('sessionStorage.json')
        storageConf = json.load(storageFile)

        for key in storageConf:
            self.driver.execute_script(
                f"sessionStorage.setItem('{key}', '{storageConf[key]}')")
