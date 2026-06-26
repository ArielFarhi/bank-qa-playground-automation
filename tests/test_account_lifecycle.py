from __future__ import annotations

import logging
from datetime import datetime, timezone

import pytest
from config import settings
from pages.account_page import AccountPage
from pages.login_page import LoginPage
from pages.transactions_page import TransactionsPage

logger = logging.getLogger(__name__)


def scenario_by_role(scenarios, role: str):
    return next(scenario for scenario in scenarios if scenario["role"] == role)


@pytest.mark.e2e
def test_admin_account_lifecycle(page, scenarios):
    scenario = scenario_by_role(scenarios, "admin")
    unique_description = (
        f"{scenario['description']} - "
        f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    )

    logger.info("Open the banking playground")
    login_page = LoginPage(page)
    login_page.open(settings.base_url)

    logger.info("Log in as user: %s", scenario["username"])
    login_page.login(scenario["username"], scenario["password"])

    logger.info("Read initial account balance: %s", scenario["account_name"])
    account_page = AccountPage(page)
    account_page.open()
    initial_balance = account_page.balance_for_account(scenario["account_name"])
    logger.info("Initial balance is %s", initial_balance)

    logger.info("Create deposit transaction: %s", scenario["deposit_amount"])
    transactions_page = TransactionsPage(page)
    transactions_page.open()
    transactions_page.create_deposit(
        scenario["account_name"],
        scenario["deposit_amount"],
        unique_description,
    )
    transactions_page.expect_latest_deposit(
        scenario["account_name"],
        scenario["deposit_amount"],
        unique_description,
    )

    expected_balance = initial_balance + scenario["deposit_amount"]
    logger.info("Validate final balance: %s", expected_balance)
    account_page.open()
    assert account_page.balance_for_account(scenario["account_name"]) == expected_balance


@pytest.mark.e2e
def test_read_only_viewer_cannot_create_transactions(page, scenarios):
    scenario = scenario_by_role(scenarios, "viewer")

    logger.info("Open the banking playground")
    login_page = LoginPage(page)
    login_page.open(settings.base_url)

    logger.info("Log in as read-only user: %s", scenario["username"])
    login_page.login(scenario["username"], scenario["password"])

    logger.info("Verify viewer can inspect account balance")
    account_page = AccountPage(page)
    account_page.open()
    account_page.balance_for_account(scenario["account_name"])

    logger.info("Verify viewer cannot create transactions")
    transactions_page = TransactionsPage(page)
    transactions_page.open()
    transactions_page.expect_transaction_creation_unavailable()
