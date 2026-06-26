from __future__ import annotations

import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class TransactionsPage(BasePage):
    @property
    def transactions_nav(self):
        return self.page.get_by_test_id("nav-transactions")

    @property
    def transaction_modal(self):
        return self.page.get_by_test_id("transaction-modal")

    @property
    def transaction_form(self):
        return self.page.get_by_test_id("transaction-form")

    @property
    def amount_input(self):
        return self.page.get_by_test_id("transaction-amount-input")

    @property
    def description_input(self):
        return self.page.get_by_test_id("transaction-description-input")

    @property
    def submit_button(self):
        return self.page.get_by_test_id("submit-transaction-button")

    def open(self) -> None:
        self.transactions_nav.click()
        expect(self.page).to_have_url(re.compile(r".*/bank/transactions$"))
        expect(self.page.get_by_test_id("transactions-table")).to_be_visible()

    def create_deposit(self, account_name: str, amount: int, description: str) -> None:
        self.page.keyboard.press("n")
        expect(self.transaction_modal).to_be_visible()
        self.transaction_form.locator("select").nth(0).select_option("deposit")
        self._select_account(account_name)
        self.amount_input.fill(str(amount))
        self.description_input.fill(description)
        expect(self.submit_button).to_be_enabled()
        self.submit_button.click()
        expect(self.page.get_by_text("Transaction completed successfully!")).to_be_visible()

    def expect_transaction_creation_unavailable(self) -> None:
        expect(self.page.get_by_test_id("new-transaction-button")).not_to_be_visible()
        self.page.keyboard.press("n")
        expect(self.transaction_modal).not_to_be_visible()

    def expect_latest_deposit(self, account_name: str, amount: int, description: str) -> None:
        latest_row = self.page.get_by_test_id("transaction-row").first
        expect(latest_row).to_contain_text("Deposit")
        expect(latest_row).to_contain_text(account_name)
        expect(latest_row).to_contain_text(f"+${amount:,.2f}")
        expect(latest_row).to_contain_text(description)

    def _select_account(self, account_name: str) -> None:
        account_select = self.transaction_form.locator("select").nth(1)
        options = account_select.locator("option")
        option_values = options.evaluate_all(
            """(items, name) => {
                const match = items.find(option => option.textContent.includes(name));
                return match ? [match.value] : [];
            }""",
            account_name,
        )
        if not option_values:
            raise AssertionError(f"Account option was not found: {account_name}")
        account_select.select_option(option_values[0])
