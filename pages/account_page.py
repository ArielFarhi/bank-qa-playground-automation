from __future__ import annotations

import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class AccountPage(BasePage):
    @property
    def accounts_nav(self):
        return self.page.get_by_test_id("nav-accounts")

    @property
    def accounts_table(self):
        return self.page.get_by_test_id("accounts-table")

    def open(self) -> None:
        self.accounts_nav.click()
        expect(self.page).to_have_url(re.compile(r".*/bank/accounts$"))
        expect(self.accounts_table).to_be_visible()

    def balance_for_account(self, account_name: str) -> float:
        row = self.page.locator("[data-testid^='account-row-']").filter(has_text=account_name)
        expect(row).to_be_visible()
        balance_text = row.get_by_test_id("account-balance").inner_text()
        return self._parse_currency(balance_text)

    @staticmethod
    def _parse_currency(value: str) -> float:
        normalized = value.replace("$", "").replace(",", "").strip()
        return float(normalized)
