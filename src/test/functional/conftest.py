"""Configuración compartida para pruebas funcionales con Selenium."""

import os

import pytest


@pytest.fixture
def base_url() -> str:
    """URL de la aplicación; se puede sobrescribir con CHAMBEAYA_BASE_URL."""
    return os.getenv("CHAMBEAYA_BASE_URL", "http://127.0.0.1:5000").rstrip("/")


@pytest.fixture
def driver():
    """Abre Chrome en modo headless y garantiza el cierre al terminar la prueba.

    Selenium Manager, integrado en Selenium 4, resuelve el driver automáticamente.
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
