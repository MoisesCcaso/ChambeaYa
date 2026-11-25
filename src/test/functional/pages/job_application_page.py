"""Page Objects for opportunities, job applications and certificate verification."""

from selenium.webdriver.common.by import By

from .base_page import BasePage


class JobApplicationPage(BasePage):
    """The intern's Opportunities and My applications views in `/app`."""

    NAV_OPPORTUNITIES = (By.CSS_SELECTOR, '[data-view="oportunidades"]')
    PANEL_OPPORTUNITIES = (By.CSS_SELECTOR, '[data-view-panel="oportunidades"]')
    OPPORTUNITY_TITLES = (By.CSS_SELECTOR, "#opportunity-list .result-item h3")
    OPPORTUNITY_DETAIL = (By.ID, "opportunity-detail")
    DETAIL_STATUS_BADGE = (By.CSS_SELECTOR, "#opportunity-detail .detail-actions .status-badge")
    NAV_APPLICATIONS = (By.CSS_SELECTOR, '[data-view="postulaciones"]')
    PANEL_APPLICATIONS = (By.CSS_SELECTOR, '[data-view-panel="postulaciones"]')
    TOAST = (By.CSS_SELECTOR, "#toast-region .toast")

    def _click(self, element) -> None:
        """Scrolls to the element and clicks it, with a JavaScript fallback."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            element,
        )
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    # --- Oportunidades ---
    def open_opportunities(self) -> "JobApplicationPage":
        """Opens Opportunities and waits for the list or the empty state."""
        self._click(self.wait_until_clickable(self.NAV_OPPORTUNITIES))
        self.wait_until_visible(self.PANEL_OPPORTUNITIES)
        self.wait_for(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR,
                "#opportunity-list .result-item, #opportunity-list .empty-state",
            )
        )
        return self

    def opportunity_titles(self) -> list[str]:
        """Titles of the job postings shown in the list."""
        return [
            heading.text.strip()
            for heading in self.driver.find_elements(*self.OPPORTUNITY_TITLES)
        ]

    def opportunity_is_listed(self, title: str) -> bool:
        """Whether the job posting appears in the opportunities list."""
        return title in self.opportunity_titles()

    def select_opportunity(self, opening_id: int) -> "JobApplicationPage":
        """Selects a job posting from the list to see its detail."""
        item = self.wait_until_clickable(
            (By.CSS_SELECTOR, f'[data-select-opening="{opening_id}"]')
        )
        self._click(item)
        self.wait_until_visible(
            (By.CSS_SELECTOR, "#opportunity-detail .detail-actions")
        )
        return self

    def apply_button_is_present(self, opening_id: int) -> bool:
        """Whether the detail offers the apply button for that job posting."""
        return bool(
            self.driver.find_elements(
                By.CSS_SELECTOR, f'[data-apply-opening="{opening_id}"]'
            )
        )

    def apply(self, opening_id: int) -> str:
        """Clicks Apply and returns the text of the notice the app shows."""
        button = self.wait_until_clickable(
            (By.CSS_SELECTOR, f'[data-apply-opening="{opening_id}"]')
        )
        self._click(button)
        return self.wait_until_visible(self.TOAST).text.strip()

    def detail_status_class(self) -> str:
        """CSS classes of the status badge that replaces the apply button."""
        return self.wait_until_visible(self.DETAIL_STATUS_BADGE).get_attribute("class")

    # --- Mis postulaciones ---
    def open_applications(self) -> "JobApplicationPage":
        """Opens the My applications view."""
        self._click(self.wait_until_clickable(self.NAV_APPLICATIONS))
        self.wait_until_visible(self.PANEL_APPLICATIONS)
        return self

    @staticmethod
    def _row_xpath(title: str) -> str:
        return (
            f'//tbody[@id="applications-table"]'
            f'//tr[.//strong[normalize-space()="{title}"]]'
        )

    def application_count(self, title: str) -> int:
        """Number of table rows for the job posting."""
        self.wait_for(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR, "#applications-table tr"
            )
        )
        return len(self.driver.find_elements(By.XPATH, self._row_xpath(title)))

    def application_has_status(self, title: str, status: str) -> bool:
        """Whether the application to the job posting shows the given status."""
        return self.wait_until_visible(
            (
                By.XPATH,
                f'{self._row_xpath(title)}//span[contains(@class, "status-{status}")]',
            )
        ).is_displayed()


class VerifyCertificatePage(BasePage):
    """Public `/verificar-certificado` view (no session required)."""

    CODE_INPUT = (By.CSS_SELECTOR, '#verify-form input[name="codigo"]')
    SUBMIT = (By.CSS_SELECTOR, '#verify-form button[type="submit"]')
    RESULT = (By.ID, "verification-result")

    def open_verification(self) -> "VerifyCertificatePage":
        """Opens the public verification page."""
        self.open("/verificar-certificado")
        self.wait_until_visible(self.CODE_INPUT)
        return self

    def verify(self, code: str) -> "VerifyCertificatePage":
        """Types the code, submits the form and waits for the result."""
        field = self.wait_until_visible(self.CODE_INPUT)
        field.clear()
        field.send_keys(code)
        self.wait_until_clickable(self.SUBMIT).click()
        self.wait_until_visible(self.RESULT)
        return self

    @property
    def result_text(self) -> str:
        """Text of the result box."""
        return self.driver.find_element(*self.RESULT).text.strip()

    @property
    def result_is_valid(self) -> bool:
        """True if the result was rendered as valid (`valid` class)."""
        classes = self.driver.find_element(*self.RESULT).get_attribute("class").split()
        return "valid" in classes
