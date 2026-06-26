# bank-qa-playground-automation

This project contains an end-to-end automation test suite for the QA Playground SecureBank application, written in Python with Playwright and Pytest.

The suite validates a full customer account lifecycle:

- Open the SecureBank application
- Log in with configured credentials
- Read the selected account balance dynamically
- Create a deposit transaction
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

The test data is stored in:

```text
data/bank_scenarios.json
```

You can change the credentials, account name, deposit amount, transaction description, and tested user roles without editing the test code.

Environment variables are also supported:

```bash
BASE_URL="https://qaplayground.com/bank"
HEADLESS=true
BROWSER=chromium
BROWSER_CHANNEL=
CHROME_PATH=
TIMEOUT_MS=15000
SLOW_MO_MS=0
RECORD_VIDEO=false
```

If Playwright browsers are not installed, you can run with a local Chrome installation:

```bash
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" pytest
```

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

An HTML report is generated automatically after each run:

```text
reports/report.html
```

If `RECORD_VIDEO=true` is enabled, videos are saved under:

```text
test-results/videos
```

## Stability Notes

The test is designed to be repeatable. It reads the initial balance at runtime and validates the expected final balance by calculating the net change from the performed operation. This avoids dependency on a fixed starting balance from previous executions.

The admin scenario covers the financial end-to-end flow. The viewer scenario covers permission handling for a read-only user.
