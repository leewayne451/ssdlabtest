"""
UI tests for the ssdlabtest auth demo, driven with Selenium against the
live app over HTTP (http://localhost:3000).
"""
import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "http://localhost:3000"


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


def fill_and_submit(driver, username, password):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "loginBtn").click()


def test_home_page_renders_login_form(driver):
    driver.get(BASE_URL)
    assert "Home & Account Creation" in driver.title
    assert driver.find_element(By.ID, "username").is_displayed()
    assert driver.find_element(By.ID, "password").is_displayed()
    assert driver.find_element(By.ID, "loginBtn").is_displayed()


def test_weak_password_shows_inline_error_and_stays_on_page(driver):
    fill_and_submit(driver, f"ui_weak_{uuid.uuid4().hex[:6]}", "weak1")

    error_text = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "errorMsg"), "8 characters")
    )
    assert error_text
    # Weak password fails the frontend check, so the page never navigates.
    assert "welcome.html" not in driver.current_url


def test_common_password_shows_backend_error(driver):
    # Long enough to pass the frontend length check, but expected to be
    # rejected by the backend dictionary check.
    fill_and_submit(driver, f"ui_common_{uuid.uuid4().hex[:6]}", "password123")

    error_text = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "errorMsg"), "common")
    )
    assert error_text
    assert "welcome.html" not in driver.current_url


def test_valid_password_creates_account_and_redirects_to_welcome(driver):
    password = "St0ngly$Unique9Pw"
    fill_and_submit(driver, f"ui_ok_{uuid.uuid4().hex[:6]}", password)

    WebDriverWait(driver, 10).until(EC.url_contains("welcome.html"))
    assert "welcome.html" in driver.current_url

    displayed_password = driver.find_element(By.ID, "displayPass").text
    assert displayed_password == password
