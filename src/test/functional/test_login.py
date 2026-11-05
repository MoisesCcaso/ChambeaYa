"""Pruebas funcionales iniciales de autenticación."""

from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_log_01_login_valido_practicante(driver, base_url):
    """Un practicante con credenciales demo accede a su panel."""
    driver.get(f"{base_url}/ingresar")
    driver.find_element(By.NAME, "email").send_keys("practicante@demo.local")
    driver.find_element(By.NAME, "password").send_keys("Demo1234")
    driver.find_element(By.CSS_SELECTOR, "#auth-form button[type='submit']").click()

    wait = WebDriverWait(driver, 10)
    wait.until(lambda browser: urlparse(browser.current_url).path == "/app")
    wait.until(
        EC.text_to_be_present_in_element((By.ID, "sidebar-role"), "Practicante")
    )

    assert urlparse(driver.current_url).path == "/app"
    assert driver.find_element(By.ID, "sidebar-role").text == "Practicante"
