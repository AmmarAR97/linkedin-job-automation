import yaml
from playwright.sync_api import sync_playwright

from utils.apply import apply_for_jobs
from utils.humanize import random_sleep
from utils.login import (
    is_logged_in,
    perform_login,
    save_cookies,
    wait_for_page_full_load,
)
from utils.search import search_easy_apply_jobs


def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f).get("automation", {})

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="./user_data",
            headless=config.get("headless", False),
            args=["--start-maximized"],
        )

        print("✅ Using existing session.")
        page = browser.new_page()
        page.goto("https://www.linkedin.com/feed/")
        wait_for_page_full_load(page)

        # Random delay for human-like behavior
        random_sleep()

        # Check login state
        if not is_logged_in(page):
            print("🔐 Session expired. Logging in again...")
            perform_login(page)
            wait_for_page_full_load(page)
            save_cookies(browser)
        else:
            print("🎉 Logged in successfully using existing session.")

        random_sleep()
        print(f"🌐 Current Page Title: {page.title()}")

        jobs = search_easy_apply_jobs(page)
        print(jobs)

        print("Applying for jobs")
        _ = apply_for_jobs(page=page, jobs=jobs)

        # input("Press Enter to close...")
        browser.close()


if __name__ == "__main__":
    main()
