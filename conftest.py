from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from config import settings


def pytest_html_report_title(report) -> None:
    report.title = "Bank QA Playground Automation Report"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.sections = [
        section
        for section in report.sections
        if not section[0].lower().startswith("captured stderr")
    ]


def pytest_configure(config) -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    Path("test-results").mkdir(exist_ok=True)

    if hasattr(config.option, "htmlpath") and not config.option.htmlpath:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        config.option.htmlpath = str(reports_dir / f"report-{timestamp}.html")


@pytest.fixture(scope="session")
def scenarios() -> list[dict[str, Any]]:
    with Path("data/bank_scenarios.json").open(encoding="utf-8") as file:
        loaded_scenarios = json.load(file)
    return [_resolve_scenario_credentials(scenario) for scenario in loaded_scenarios]


def _resolve_scenario_credentials(scenario: dict[str, Any]) -> dict[str, Any]:
    resolved_scenario = scenario.copy()
    missing_env_vars = []
    for field in ("username", "password"):
        env_var = resolved_scenario.pop(f"{field}_env", None)
        if not env_var:
            continue
        value = os.getenv(env_var)
        if value is None:
            missing_env_vars.append(env_var)
            continue
        resolved_scenario[field] = value

    if missing_env_vars:
        role = resolved_scenario.get("role", "unknown")
        missing = ", ".join(missing_env_vars)
        raise pytest.UsageError(
            f"Missing environment variables for {role} scenario: {missing}"
        )

    return resolved_scenario


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    browser_launcher = getattr(playwright_instance, settings.browser)
    launch_options = {
        "headless": settings.headless,
        "slow_mo": settings.slow_mo_ms,
    }
    if settings.browser_channel:
        launch_options["channel"] = settings.browser_channel
    if settings.executable_path:
        launch_options["executable_path"] = settings.executable_path
    browser = browser_launcher.launch(
        **launch_options,
    )
    yield browser
    browser.close()


@pytest.fixture()
def page(browser: Browser) -> Page:
    context_options = {"viewport": {"width": 1440, "height": 900}}
    if settings.record_video:
        context_options["record_video_dir"] = "test-results/videos"
    context = browser.new_context(**context_options)
    page = context.new_page()
    page.set_default_timeout(settings.timeout_ms)
    yield page
    context.close()
