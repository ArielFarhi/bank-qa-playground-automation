# bank-qa-playground-automation

This project contains an end-to-end automation test suite for the QA Playground SecureBank application, written in Python with Playwright and Pytest.

The suite validates a full customer account lifecycle:

- Open the SecureBank application
- Log in with configured credentials
- Read the selected account balance dynamically
- Create a deposit transaction
- Create a withdrawal transaction
- Validate the latest transaction row
- Validate the final account balance by delta, not by a hardcoded account state
- Verify that a read-only viewer can inspect account data but cannot create transactions

## Project Structure

```text
.
├── config.py
├── conftest.py
├── data/
│   └── bank_scenarios.json
├── pages/
│   ├── account_page.py
│   ├── base_page.py
│   ├── login_page.py
│   └── transactions_page.py
├── tests/
│   └── test_account_lifecycle.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- pip

## First-Time Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install
```

## Configuration

The non-secret test data is stored in:

```text
data/bank_scenarios.json
```

Credentials are read from environment variables. Keep local values in a `.env` file or export them in your shell/CI secret store. Local `.env` values are loaded automatically before the tests run. The repository includes `.env.example` with the required variable names, but `.env` itself is ignored by git.

Required credential variables:

```bash
BANK_ADMIN_USERNAME=
BANK_ADMIN_PASSWORD=
BANK_VIEWER_USERNAME=
BANK_VIEWER_PASSWORD=
```

You can change the account name, deposit amount, withdrawal amount, transaction descriptions, and tested user roles without editing the test code. To use different credential variable names per scenario, update the `username_env` and `password_env` values in `data/bank_scenarios.json`.

Environment variables are also supported:

```bash
BANK_ADMIN_USERNAME="<admin-username>"
BANK_ADMIN_PASSWORD="<admin-password>"
BANK_VIEWER_USERNAME="<viewer-username>"
BANK_VIEWER_PASSWORD="<viewer-password>"
BASE_URL="https://qaplayground.com/bank"
HEADLESS=true
BROWSER=chromium
TIMEOUT_MS=15000
SLOW_MO_MS=0
RECORD_VIDEO=false
```

If Playwright browsers are not installed, you can run with a local Chrome installation:

```bash
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" pytest
```

`BROWSER_CHANNEL` and `CHROME_PATH` are optional browser overrides. Leave them unset for the default Playwright-managed Chromium browser.

## Running the Tests

Run the full suite:

```bash
pytest
```

Run with a visible browser:

```bash
HEADLESS=false pytest
```

Run only end-to-end tests:

```bash
pytest -m e2e
```

## Reporting

An HTML report is generated automatically after each run under `reports/`.
Each run gets a timestamped file so recent reports remain available for comparison:

```text
reports/report-YYYYMMDD-HHMMSS.html
```

The `reports/` directory is ignored by git because it contains generated run artifacts.
The report includes a readable execution scope summary, scenario descriptions, captured test logs, and redacted credentials on failure. Failed tests also save a screenshot and Playwright trace under `test-results/` for debugging dynamic UI, loading, or network-related issues.

If `RECORD_VIDEO=true` is enabled, videos are saved under:

```text
test-results/videos
```

Failure diagnostics are saved under:

```text
test-results/screenshots
test-results/traces
```

## Stability Notes

The test is designed to be repeatable. It reads the initial balance at runtime and validates the expected final balance by calculating the net change from the performed operation. This avoids dependency on a fixed starting balance from previous executions.

The admin scenario covers the financial end-to-end flow. The viewer scenario covers permission handling for a read-only user.
