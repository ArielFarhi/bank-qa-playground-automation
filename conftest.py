from __future__ import annotations

import base64
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from pytest_html import extras as html_extras
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from config import settings


class SecretValue(str):
    def __repr__(self) -> str:
        return "'***REDACTED***'"


def pytest_html_report_title(report) -> None:
    report.title = "SecureBank Automation Test Report"


def pytest_html_results_summary(prefix, summary, postfix, session) -> None:
    prefix.extend(
        [
            '<section class="summary-card">',
            "<strong>Execution scope</strong>",
            "<ul>",
            "<li>Admin end-to-end flow: login, balance read, deposit, withdrawal, and final balance validation.</li>",
            "<li>Viewer authorization flow: read-only access is allowed, transaction creation is blocked.</li>",
            "<li>Credentials are loaded from environment variables and redacted from failure output.</li>",
            "</ul>",
            "</section>",
        ]
    )


def pytest_html_results_table_header(cells) -> None:
    cells.insert(2, '<th class="sortable scenario" data-column-type="scenario">Scenario</th>')
    cells.pop()


def pytest_html_results_table_row(report, cells) -> None:
    cells.insert(2, f'<td class="col-scenario">{_scenario_title(report.nodeid)}</td>')
    cells.pop()


def _scenario_title(nodeid: str) -> str:
    titles = {
        "test_admin_account_lifecycle": (
            "Admin account lifecycle: deposit, withdrawal, balance validation"
        ),
        "test_read_only_viewer_cannot_create_transactions": (
            "Viewer permissions: inspect accounts, block transaction creation"
        ),
    }
    for test_name, title in titles.items():
        if test_name in nodeid:
            return title
    return "Automation scenario"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.sections = [
        section
        for section in report.sections
        if not section[0].lower().startswith("captured stderr")
    ]
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" and report.failed:
        _add_failure_diagnostics(item, report)


def pytest_configure(config) -> None:
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    Path("test-results").mkdir(exist_ok=True)
    Path("test-results/screenshots").mkdir(parents=True, exist_ok=True)
    Path("test-results/traces").mkdir(parents=True, exist_ok=True)

    if hasattr(config.option, "htmlpath") and not config.option.htmlpath:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        config.option.htmlpath = str(reports_dir / f"report-{timestamp}.html")


def _add_failure_diagnostics(item, report) -> None:
    page = getattr(item, "_page", None)
    if page:
        screenshot_path, screenshot_bytes = _capture_failure_screenshot(item, page)
        if screenshot_path and screenshot_bytes:
            extras = getattr(report, "extras", [])
            extras.append(
                html_extras.png(
                    base64.b64encode(screenshot_bytes).decode("ascii"),
                    name="Failure screenshot",
                )
            )
            report.extras = extras

        trace_path = _stop_failure_trace(item, page)
        if trace_path:
            report.sections.append(("playwright trace", str(trace_path)))


def _capture_failure_screenshot(item, page: Page) -> tuple[Path | None, bytes | None]:
    screenshot_path = _artifact_path("screenshots", item.nodeid, "png")
    try:
        screenshot_bytes = page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception:
        return None, None
    return screenshot_path, screenshot_bytes


def _stop_failure_trace(item, page: Page) -> Path | None:
    if not getattr(item, "_trace_started", False) or getattr(item, "_trace_stopped", False):
        return None

    trace_path = _artifact_path("traces", item.nodeid, "zip")
    try:
        page.context.tracing.stop(path=str(trace_path))
    except Exception:
        return None

    item._trace_stopped = True
    return trace_path


def _artifact_path(kind: str, nodeid: str, extension: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_nodeid = re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid).strip("_")[:140]
    return Path("test-results") / kind / f"{safe_nodeid}-{timestamp}.{extension}"


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
        resolved_scenario[field] = SecretValue(value) if field == "password" else value

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
def page(browser: Browser, request) -> Page:
    context_options = {"viewport": {"width": 1440, "height": 900}}
    if settings.record_video:
        context_options["record_video_dir"] = "test-results/videos"
    context = browser.new_context(**context_options)
    request.node._trace_started = False
    request.node._trace_stopped = False
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    request.node._trace_started = True

    page = context.new_page()
    request.node._page = page
    page.set_default_timeout(settings.timeout_ms)

    yield page

    if request.node._trace_started and not request.node._trace_stopped:
        context.tracing.stop()
    context.close()
