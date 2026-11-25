"""Page Object for the Profile view (/app -> Perfil)."""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base_page import BasePage


class ProfilePage(BasePage):
    """Actions and selectors for the intern and company profile view."""

    NAV_PROFILE = (By.CSS_SELECTOR, '[data-view="perfil"]')
    PANEL_PROFILE = (By.CSS_SELECTOR, '[data-view-panel="perfil"]')

    # Perfil Practicante
    STUDENT_FORM = (By.ID, "student-profile-form")
    STUDENT_FIRST_NAMES = (By.CSS_SELECTOR, '#student-profile-form input[name="nombres"]')
    STUDENT_LAST_NAMES = (By.CSS_SELECTOR, '#student-profile-form input[name="apellidos"]')
    STUDENT_DNI = (By.CSS_SELECTOR, '#student-profile-form input[name="dni"]')
    STUDENT_ID_CARD = (By.CSS_SELECTOR, '#student-profile-form input[name="carnet_universitario"]')
    STUDENT_SUBMIT = (By.CSS_SELECTOR, '#student-profile-form button[type="submit"]')
    STUDENT_STATUS = (By.ID, "student-profile-status")

    # Habilidades
    SKILL_INPUT = (By.ID, "skill-input")
    ADD_SKILL_BUTTON = (By.ID, "add-skill")
    SKILLS_LIST = (By.ID, "skills-list")

    # Education
    EDUCATION_INPUT = (By.ID, "education-input")
    ADD_EDUCATION_BUTTON = (By.ID, "add-education")
    EDUCATION_LIST = (By.ID, "education-list")

    # Perfil Empresa
    COMPANY_FORM = (By.ID, "company-profile-form")
    COMPANY_LEGAL_NAME = (By.CSS_SELECTOR, '#company-profile-form input[name="razon_social"]')
    COMPANY_RUC = (By.CSS_SELECTOR, '#company-profile-form input[name="ruc"]')
    COMPANY_SUBMIT = (By.CSS_SELECTOR, '#company-profile-form button[type="submit"]')
    COMPANY_STATUS = (By.ID, "company-profile-status")

    # Notificaciones / Feedback
    TOAST = (By.CSS_SELECTOR, "#toast-region .toast")

    def _click(self, element) -> None:
        """Scrolls to the element and clicks it robustly."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element
        )
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def open_profile(self) -> "ProfilePage":
        """Navigates to the profile view in /app."""
        btn = self.wait_until_clickable(self.NAV_PROFILE)
        self._click(btn)
        self.wait_until_visible(self.PANEL_PROFILE)
        return self

    def _set_input(self, locator, value: str) -> None:
        """Clears the input with control+a and types the new value."""
        el = self.wait_until_visible(locator)
        self._click(el)
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.BACKSPACE)
        if value:
            el.send_keys(value)

    def fill_student_profile(
        self,
        first_names: str | None = None,
        last_names: str | None = None,
        dni: str | None = None,
        card: str | None = None,
    ) -> "ProfilePage":
        """Fills in the intern form."""
        if first_names is not None:
            self._set_input(self.STUDENT_FIRST_NAMES, first_names)
        if last_names is not None:
            self._set_input(self.STUDENT_LAST_NAMES, last_names)
        if dni is not None:
            self._set_input(self.STUDENT_DNI, dni)
        if card is not None:
            self._set_input(self.STUDENT_ID_CARD, card)
        return self

    def submit_student_profile(self) -> None:
        """Submits the intern form."""
        btn = self.wait_until_clickable(self.STUDENT_SUBMIT)
        self._click(btn)

    def get_student_status(self) -> str:
        """Gets the intern save/notification status text."""
        status_el = self.driver.find_element(*self.STUDENT_STATUS)
        text = status_el.text.strip()
        if text:
            return text
        toast = self.wait_until_visible(self.TOAST)
        return toast.text.strip()

    def remove_skill_if_present(self, skill_name: str) -> "ProfilePage":
        """Removes a skill from the list if it is already there."""
        skills_container = self.wait_until_visible(self.SKILLS_LIST)
        tags = skills_container.find_elements(By.CSS_SELECTOR, ".tag")
        for tag in tags:
            if skill_name.lower() in tag.text.lower():
                remove_btn = tag.find_element(By.CSS_SELECTOR, "button[data-remove-skill]")
                self._click(remove_btn)
                break
        return self

    def add_skill(self, skill_name: str) -> "ProfilePage":
        """Adds a skill to the intern profile."""
        self._set_input(self.SKILL_INPUT, skill_name)
        btn = self.wait_until_clickable(self.ADD_SKILL_BUTTON)
        self._click(btn)
        return self

    def get_skills(self) -> list[str]:
        """Gets the current list of skills shown as tags."""
        skills_container = self.wait_until_visible(self.SKILLS_LIST)
        tags = skills_container.find_elements(By.CSS_SELECTOR, ".tag")
        return [tag.text.strip() for tag in tags if tag.text.strip()]

    def remove_education_if_present(self, education_name: str) -> "ProfilePage":
        """Removes an education entry from the list if it is already there."""
        edu_container = self.wait_until_visible(self.EDUCATION_LIST)
        tags = edu_container.find_elements(By.CSS_SELECTOR, ".tag")
        for tag in tags:
            if education_name.lower() in tag.text.lower():
                remove_btn = tag.find_element(By.CSS_SELECTOR, "button[data-remove-education]")
                self._click(remove_btn)
                break
        return self

    def add_education(self, education_name: str) -> "ProfilePage":
        """Adds an education entry to the intern profile."""
        self._set_input(self.EDUCATION_INPUT, education_name)
        btn = self.wait_until_clickable(self.ADD_EDUCATION_BUTTON)
        self._click(btn)
        return self

    def get_education(self) -> list[str]:
        """Gets the current list of education entries shown as tags."""
        edu_container = self.wait_until_visible(self.EDUCATION_LIST)
        tags = edu_container.find_elements(By.CSS_SELECTOR, ".tag")
        return [tag.text.strip() for tag in tags if tag.text.strip()]

    def fill_company_profile(
        self,
        legal_name: str | None = None,
        ruc: str | None = None,
    ) -> "ProfilePage":
        """Fills in the company form."""
        if legal_name is not None:
            self._set_input(self.COMPANY_LEGAL_NAME, legal_name)
        if ruc is not None:
            self._set_input(self.COMPANY_RUC, ruc)
        return self

    def submit_company_profile(self) -> None:
        """Submits the company form."""
        btn = self.wait_until_clickable(self.COMPANY_SUBMIT)
        self._click(btn)

    def get_company_status(self) -> str:
        """Gets the company save/notification status text."""
        status_el = self.driver.find_element(*self.COMPANY_STATUS)
        text = status_el.text.strip()
        if text:
            return text
        toast = self.wait_until_visible(self.TOAST)
        return toast.text.strip()

    def is_company_ruc_valid(self) -> bool:
        """Whether the RUC field meets the browser (HTML5) constraints."""
        ruc_el = self.driver.find_element(*self.COMPANY_RUC)
        return self.driver.execute_script("return arguments[0].validity.valid;", ruc_el)

    def company_ruc_validation_message(self) -> str:
        """Returns the browser's native validation message for RUC."""
        ruc_el = self.driver.find_element(*self.COMPANY_RUC)
        return self.driver.execute_script("return arguments[0].validationMessage;", ruc_el)

    def get_company_ruc_value(self) -> str:
        """Returns the current value of the RUC field."""
        ruc_el = self.driver.find_element(*self.COMPANY_RUC)
        return ruc_el.get_attribute("value")
