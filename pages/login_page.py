from __future__ import annotations

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
        expect(self.page.get_by_test_id("welcome-message")).to_contain_text(
            f"Welcome back, {username}!"
        )
