"""Page Object to create and query company job postings."""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base_page import BasePage


class JobPostingPage(BasePage):
    """Actions and queries for the job postings view in `/app`."""

    MENU = (By.CSS_SELECTOR, '[data-view="convocatorias"]')
    PANEL = (By.CSS_SELECTOR, '[data-view-panel="convocatorias"]')
    NEW_BUTTON = (By.ID, "new-opening-button")
    DIALOG = (By.ID, "opening-dialog")
    FORM = (By.ID, "opening-form")
    TITLE = (By.NAME, "titulo")
    DESCRIPTION = (By.NAME, "descripcion")
    SKILLS = (By.NAME, "habilidades_requeridas")
    BENEFITS = (By.NAME, "beneficios")
    SAVE_BUTTON = (By.CSS_SELECTOR, '#opening-form button[type="submit"]')
    TABLE = (By.ID, "openings-table")
    TOAST_CLOSE_BUTTONS = (By.CSS_SELECTOR, '#toast-region .toast button[aria-label="Cerrar"]')

    def open_job_postings(self) -> "JobPostingPage":
        """Opens the job postings section from the company menu."""
        self.wait_until_clickable(self.MENU).click()
        self.wait_until_visible(self.PANEL)
        return self

    def start_new_job_posting(self) -> "JobPostingPage":
        """Opens the modal form to create a job posting."""
        self.wait_until_clickable(self.NEW_BUTTON).click()
        self.wait_until_visible(self.DIALOG)
        return self

    def fill_job_posting(
        self,
        title: str,
        description: str = "",
        skills: str = "",
        benefits: str = "",
    ) -> "JobPostingPage":
        """Fills in the job posting form fields."""
        fields = (
            (self.TITLE, title),
            (self.DESCRIPTION, description),
            (self.SKILLS, skills),
            (self.BENEFITS, benefits),
        )
        for locator, value in fields:
            field = self.wait_until_visible(locator)
            field.clear()
            field.send_keys(value)
        return self

    def save_draft(self) -> None:
        """Saves the form as a draft."""
        self.wait_until_clickable(self.SAVE_BUTTON).click()

    def create_draft(
        self,
        title: str,
        description: str = "",
        skills: str = "",
        benefits: str = "",
    ) -> None:
        """Fills in and saves a new job posting as a draft."""
        self.start_new_job_posting()
        self.fill_job_posting(title, description, skills, benefits)
        self.save_draft()
        self.wait_for(
            lambda _driver: self.driver.find_element(*self.DIALOG).get_attribute(
                "open"
            ) is None
        )
        self.job_posting_row(title)

    def job_posting_row(self, title: str):
        """Returns the table row for the given title."""
        return self.wait_until_visible(
            (
                By.XPATH,
                f'//tbody[@id="openings-table"]//tr[.//strong[normalize-space()="{title}"]]'
            )
        )

    def job_posting_is_draft(self, title: str) -> bool:
        """Whether the job posting row shows the draft status."""
        return "borrador" in self.job_posting_row(title).text.casefold()

    def publish_job_posting(self, title: str) -> None:
        """Publishes the draft identified by its title and waits for the update."""
        self._dismiss_toasts()
        row = self.job_posting_row(title)
        publish_button = row.find_element(
            By.CSS_SELECTOR, "[data-publish-opening]"
        )
        publish_button.send_keys(Keys.ENTER)
        self.wait_until_visible(
            (
                By.XPATH,
                f'//tbody[@id="openings-table"]//tr[.//strong[normalize-space()="{title}"]]//span[contains(@class, "status-publicada")]',
            )
        )

    def job_posting_is_published(self, title: str) -> bool:
        """Whether the table shows the job posting as published."""
        return self.wait_until_visible(
            (
                By.XPATH,
                f'//tbody[@id="openings-table"]//tr[.//strong[normalize-space()="{title}"]]//span[contains(@class, "status-publicada")]',
            )
        ).is_displayed()

    def can_publish_job_posting(self, title: str) -> bool:
        """Whether the job posting row offers the Publish action."""
        row = self.job_posting_row(title)
        return bool(row.find_elements(By.CSS_SELECTOR, "[data-publish-opening]"))

    def close_job_posting(self, title: str) -> None:
        """Closes a published job posting and waits for the updated status."""
        self._dismiss_toasts()
        row = self.job_posting_row(title)
        close_button = row.find_element(By.CSS_SELECTOR, "[data-close-opening]")
        close_button.send_keys(Keys.ENTER)
        self.wait_until_visible(
            (
                By.XPATH,
                f'//tbody[@id="openings-table"]//tr[.//strong[normalize-space()="{title}"]]//span[contains(@class, "status-cerrada")]',
            )
        )

    def job_posting_is_closed(self, title: str) -> bool:
        """Whether the table shows the job posting as closed."""
        return self.wait_until_visible(
            (
                By.XPATH,
                f'//tbody[@id="openings-table"]//tr[.//strong[normalize-space()="{title}"]]//span[contains(@class, "status-cerrada")]',
            )
        ).is_displayed()

    def open_candidates(self, title: str) -> None:
        """Opens the candidate list of a published or closed job posting."""
        row = self.job_posting_row(title)
        row.find_element(By.CSS_SELECTOR, "[data-candidates-opening]").click()
        self.wait_until_visible((By.ID, "candidates-dialog"))
        self.wait_for(
            lambda browser: browser.find_elements(
                By.CSS_SELECTOR,
                "#candidate-list .candidate-row, #candidate-list .empty-state",
            )
        )

    def candidate_names(self) -> list[str]:
        """Returns the names shown in the candidate list."""
        return [
            heading.text.strip()
            for heading in self.driver.find_elements(
                By.CSS_SELECTOR, "#candidate-list .candidate-row h3"
            )
        ]

    def candidate_is_listed(self, name: str) -> bool:
        """Whether the given name appears among the candidates."""
        return name in self.candidate_names()

    def _dismiss_toasts(self) -> None:
        """Closes floating notices that could cover the table controls."""
        for button in self.driver.find_elements(*self.TOAST_CLOSE_BUTTONS):
            button.click()
