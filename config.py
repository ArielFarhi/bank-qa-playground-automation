from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv(
        "BASE_URL",
        "https://qaplayground.com/bank",
    )
    headless: bool = os.getenv("HEADLESS", "true").lower() in {"1", "true", "yes"}
    browser: str = os.getenv("BROWSER", "chromium")
    browser_channel: str | None = os.getenv("BROWSER_CHANNEL") or None
    executable_path: str | None = os.getenv("CHROME_PATH") or None
    timeout_ms: int = int(os.getenv("TIMEOUT_MS", "15000"))
    slow_mo_ms: int = int(os.getenv("SLOW_MO_MS", "0"))
    record_video: bool = os.getenv("RECORD_VIDEO", "false").lower() in {"1", "true", "yes"}


settings = Settings()
