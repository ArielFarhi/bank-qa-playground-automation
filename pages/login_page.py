from __future__ import annotations

import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    @property
    def username_input(self):
        return self.page.locator("#username")

    @property
    def password_input(self):
        return self.page.locator("#password")

    @property
    def login_button(self):
        return self.page.get_by_test_id("login-button")

    def open(self, base_url: str) -> None:
        self.goto(base_url)
        expect(self.username_input).to_be_visible()

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        expect(self.login_button).to_be_enabled()
        self.login_button.click()
        welcome_message = self.page.get_by_test_id("welcome-message")
        try:
            expect(self.page).to_have_url(re.compile(r".*/bank/dashboard$"), timeout=5000)
            expect(welcome_message).to_contain_text(f"Welcome back, {username}!")
        except AssertionError as error:
            raise AssertionError(
                "Login failed with the configured credentials. "
                "Verify the username/password environment variables in .env or CI secrets."
            ) from error
