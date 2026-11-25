"""Shared configuration for the Selenium functional tests."""

import os

import pytest


@pytest.fixture
def base_url() -> str:
    """App URL; can be overridden with CHAMBEAYA_BASE_URL."""
    return os.getenv("CHAMBEAYA_BASE_URL", "http://127.0.0.1:5000").rstrip("/")


@pytest.fixture
def driver():
    """Opens headless Chrome and makes sure it closes when the test ends.

    Selenium Manager, built into Selenium 4, resolves the driver automatically.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1000")

    browser = webdriver.Chrome(options=options)
    try:
        yield browser
    finally:
        browser.quit()
