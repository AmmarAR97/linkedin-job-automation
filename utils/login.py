import os

import yaml
from dotenv import load_dotenv
from playwright.sync_api import Page

from utils.humanize import (
    human_click,
    human_type,
    random_sleep,
    wait_for_page_full_load,
)

load_dotenv()


LINKEDIN_EMAIL: str = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD: str = os.getenv("LINKEDIN_PASSWORD", "")


with open("config.yaml") as f:
    config = yaml.safe_load(f)


def linkedin_login(p):
    """Logs into LinkedIn and saves session for reuse."""

    headless = config["linkedin"]["headless"]

    browser = p.chromium.launch(headless=headless)
    context = browser.new_context()

    page = context.new_page()
    page.goto("https://www.linkedin.com/login", wait_until="load")
    wait_for_page_full_load(page)

    human_type(page, "#username", LINKEDIN_EMAIL)
    random_sleep(0.2, 0.6)
    human_type(page, "#password", LINKEDIN_PASSWORD)

    human_click(page, "button[type=submit]")
    wait_for_page_full_load(page)

    print("✅ Logged in successfully.")

    return context


def is_logged_in(page: Page) -> bool:
    """Detect if the user is logged in based on presence of LinkedIn feed"""
    try:
        page.wait_for_function(
            "document.title && document.title.includes('Feed | LinkedIn')", timeout=5000
        )
        return True
    except Exception:
        return False


def perform_login(page: Page):
    """Perform LinkedIn login manually."""
    page.goto("https://www.linkedin.com/login")
    wait_for_page_full_load(page)

    human_type(page, "#username", LINKEDIN_EMAIL)
    random_sleep(0.2, 0.6)

    human_type(page, "#password", LINKEDIN_PASSWORD)

    human_click(page, "button[type=submit]")

    wait_for_page_full_load(page)
    print("✅ Login complete!")


def save_cookies(browser_context):
    path = "./user_data/cookies.json"
    _ = browser_context.storage_state(path=path)
    print(f"💾 Cookies saved to {path}")


def load_cookies(browser_context):
    path = "./user_data/cookies.json"
    try:
        browser_context.add_cookies(path)
        print(f"🍪 Loaded cookies from {path}")
    except Exception:
        print("⚠️ No cookies found or invalid file.")
