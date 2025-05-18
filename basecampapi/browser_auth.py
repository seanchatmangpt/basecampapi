import time
from urllib.parse import urlparse, parse_qs

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class BrowserAuth:
    """Automate Basecamp authentication using a browser.

    Parameters
    ----------
    credentials : dict
        Dictionary containing ``client_id``, ``client_secret`` and
        ``redirect_uri``.
    username : str
        Basecamp username.
    password : str
        Basecamp password.
    headless : bool, optional
        Run browser in headless mode, by default ``True``.
    """

    def __init__(self, credentials: dict, username: str, password: str, headless: bool = True):
        self.credentials = credentials
        self.username = username
        self.password = password
        self.headless = headless

    def get_tokens(self) -> dict:
        """Return refreshed credentials containing ``access_token`` and ``refresh_token``."""

        verification_url = (
            "https://launchpad.37signals.com/authorization/new?type=web_server"
            f"&client_id={self.credentials['client_id']}"
            f"&redirect_uri={self.credentials['redirect_uri']}"
        )

        options = Options()
        if self.headless:
            options.add_argument("--headless")

        # NOTE: Requires a webdriver installed and available on PATH.
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(verification_url)
            # The element identifiers may change, update them if necessary.
            driver.find_element(By.ID, "username").send_keys(self.username)
            driver.find_element(By.ID, "password").send_keys(self.password)
            driver.find_element(By.NAME, "commit").click()

            # Wait for redirection to the provided redirect URI
            time.sleep(5)
            redirect_url = driver.current_url
        finally:
            driver.quit()

        code_list = parse_qs(urlparse(redirect_url).query).get("code")
        if not code_list:
            raise Exception("Could not obtain verification code from redirect URL.")
        code = code_list[0]

        token_url = (
            "https://launchpad.37signals.com/authorization/token?type=web_server"
            f"&client_id={self.credentials['client_id']}"
            f"&redirect_uri={self.credentials['redirect_uri']}"
            f"&client_secret={self.credentials['client_secret']}"
            f"&code={code}"
        )

        response = requests.post(token_url)
        if not response.ok:
            raise Exception(
                f"Status code: {response.status_code}. {response.reason}. Error text: {response.text}."
            )

        data = response.json()
        self.credentials["refresh_token"] = data["refresh_token"]
        self.credentials["access_token"] = data["access_token"]
        return self.credentials

