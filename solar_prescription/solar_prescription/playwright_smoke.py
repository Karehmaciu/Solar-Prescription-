"""Playwright UI smoke test.

Runs the Flask app (if not already running) and drives the UI like a user:
- sets a location (without relying on external geocoding)
- selects a 10W kit
- selects 1 LED bulb + 1 phone charge
- submits
- asserts the results show 'Too Small' and that tested-value note is shown

Usage:
  python playwright_smoke.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright


SMOKE_PORT = int(os.environ.get("SMOKE_PORT", "5051"))
BASE_URL = f"http://127.0.0.1:{SMOKE_PORT}"


def _wait_for_http_ok(url: str, timeout_s: float = 20) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def _start_server() -> subprocess.Popen:
    """Start a fresh Flask server for the smoke test on SMOKE_PORT."""
    app_py = Path(__file__).with_name("app.py")
    env = os.environ.copy()
    env["PORT"] = str(SMOKE_PORT)

    # Start server without reloader
    proc = subprocess.Popen(
        [sys.executable, str(app_py)],
        cwd=str(app_py.parent),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if not _wait_for_http_ok(f"{BASE_URL}/", timeout_s=20):
        try:
            if proc.stdout:
                output = proc.stdout.read()
            else:
                output = ""
        except Exception:
            output = ""
        proc.terminate()
        raise RuntimeError(f"Flask server did not start on {BASE_URL}. Output:\n{output}")

    return proc


def main() -> int:
    proc = None
    try:
        proc = _start_server()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(f"{BASE_URL}/", wait_until="domcontentloaded")

            # Fill required visible input
            page.fill("#locationSearch", "Nyeri, Kenya")

            # Bypass external geocoding: set hidden inputs directly.
            # Nyeri (approx)
            page.evaluate(
                """() => {
                    document.querySelector('#latitude').value = '-0.4167';
                    document.querySelector('#longitude').value = '36.9500';
                    document.querySelector('#locationName').value = 'Nyeri, Kenya';
                }"""
            )

            # Select kit size 10W
            # Inputs are styled/hidden; click the visible card.
            page.locator('label.kit-size-option:has(input[name="kitSize"][value="10"])').click()

            # Select appliances + set quantities
            page.locator('label.appliance-option:has(input[name="appliance"][value="led_bulb"])').click()
            page.fill('#qty_led_bulb', '1')

            page.locator('label.appliance-option:has(input[name="appliance"][value="phone_charger"])').click()
            page.fill('#qty_phone', '1')

            # Submit
            page.click('#submitBtn')

            # Wait for redirect to results
            page.wait_for_url("**/results", timeout=30000)

            body_text = page.inner_text("body")
            assert "This Kit is Too Small" in body_text

            # The sizing recommendation should be based on worst-month usable energy.
            # For 10W + (1 bulb + 1 phone), this should recommend at least 50W.
            assert "Minimum recommended: 50W" in body_text

            browser.close()

        print("OK: Playwright smoke test passed")
        return 0

    finally:
        if proc is not None:
            proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
