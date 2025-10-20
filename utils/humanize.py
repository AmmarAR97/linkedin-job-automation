import random
import time

import yaml
from playwright.sync_api import Page

with open("config.yaml") as f:
    config = yaml.safe_load(f)["automation"]


def random_sleep(min_s=None, max_s=None):
    """
    Sleep for a random duration between min_s and max_s (seconds).
    If not provided, uses values from config.
    """
    min_s = config["min_action_delay"]
    max_s = config["max_action_delay"]
    # small skew: sample from a beta-like distribution to favor shorter waits but allow long tails
    u = random.random()
    # bias a bit toward shorter durations
    bias = u**1.4
    wait = min_s + bias * (max_s - min_s)
    time.sleep(wait)
    return wait


def human_type(page: Page, selector: str, text: str):
    """
    Type text into input like a human: uses per-keystroke delay randomized by config.
    Falls back to page.fill if typing is too slow for big text like a resume field.
    """
    if not text:
        return
    # if the text is long, it's often better to fill directly after a short pause
    if len(text) > 200:
        random_sleep(0.2, 0.8)
        page.fill(selector, text)
        random_sleep()
        return

    # per-char delay in ms
    min_ms = config["typing_delay_min"]
    max_ms = config["typing_delay_max"]

    # choose a per-keystroke delay
    delay = random.randint(min_ms, max_ms)

    page.click(selector)  # focus
    random_sleep(0.05, 0.2)
    page.type(selector, text, delay=delay)  # ms per char
    random_sleep()


def human_click(page: Page, selector: str, timeout=30000):
    """
    Click an element like a human: wait for it, move mouse a bit (if available), then click.
    Uses random_sleep before and after click to mimic human reaction.
    """
    # small pre-click random pause
    random_sleep()
    locator = page.locator(selector)
    locator.wait_for(state="visible", timeout=timeout)
    try:
        # Try a real click
        locator.click()
    except Exception:
        # fallback: use JS click (less human-like but robust)
        page.evaluate("el => el.click()", locator.element_handle())
    random_sleep()


def wait_for_page_full_load(page, selector=None, timeout=45000):
    """
    Wait for full load on pages like LinkedIn that constantly make background requests.
    - Waits for DOM + load.
    - Optionally waits for a key selector (e.g. main content).
    - Then sleeps a randomized buffer.
    """
    page.wait_for_load_state("domcontentloaded", timeout=timeout)
    page.wait_for_load_state("load", timeout=timeout)

    # Optional: wait for main content or feed to be visible
    if selector:
        try:
            page.wait_for_selector(selector, timeout=timeout)
        except Exception:
            print(f"⚠️ Selector {selector} not found within {timeout} ms.")

    # Add a realistic random pause
    extra_delay = random.uniform(2.5, 5.0)
    print(f"🕐 Waiting an extra {extra_delay:.2f}s for async UI rendering...")
    time.sleep(extra_delay)
