from __future__ import annotations

from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def wait_until_ready(self) -> None:
        expect(self.page.locator("body")).to_be_visible()
