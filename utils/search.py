import yaml

from utils.humanize import random_sleep
from utils.login import wait_for_page_full_load

with open("config.yaml") as f:
    config = yaml.safe_load(f)["job_search"]


def search_easy_apply_jobs(page, scroll_times=10):
    print("🔍 Searching for Easy Apply jobs")
    page.goto(config["url"])
    wait_for_page_full_load(page)
    random_sleep()

    # Find the scroll container after the sentinel div
    sentinel = page.query_selector("div[data-results-list-top-scroll-sentinel]")
    if not sentinel:
        raise Exception("❌ Could not find job results sentinel container.")

    # The next sibling <ul> is the job list container (dynamic class name)
    ul_container = sentinel.evaluate_handle("el => el.nextElementSibling")
    if not ul_container:
        raise Exception("❌ Could not find job list container <ul>.")

    # Bring the UL into view and focus it to simulate human interaction
    page.evaluate(
        "(el) => el.scrollIntoView({block: 'center', inline: 'center'})", ul_container
    )
    page.evaluate("(el) => el.focus()", ul_container)
    random_sleep()

    # Move mouse over it
    box = ul_container.bounding_box()
    print("Box:", box)
    if box:
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        print("🖱️ Hovered and focused job list container.")

    # Perform controlled scrolls inside the UL container
    for i in range(scroll_times):
        print(f"📜 Scrolling job list... ({i + 1}/{scroll_times})")
        page.evaluate(
            """(ul) => { ul.scrollBy(0, ul.scrollHeight / 2); }""", ul_container
        )
        random_sleep()

    # Extract job cards
    print("🔍 Extracting visible job cards...")

    jobs = []
    job_divs = page.query_selector_all("div[data-job-id]")

    if not job_divs:
        print("⚠️ No job cards found. Trying fallback selector...")
        job_divs = page.query_selector_all(
            "li[data-occludable-job-id] div.job-card-container"
        )

    print(f"🧩 Found {len(job_divs)} job card containers.")

    for div in job_divs:
        try:
            title_el = div.query_selector("a.job-card-container__link")
            company_el = div.query_selector(".artdeco-entity-lockup__subtitle")
            easy_apply_el = div.query_selector("li:has-text('Easy Apply')")

            title = (
                title_el.inner_text().split("\n")[0].strip().strip()
                if title_el
                else "Unknown"
            )
            link = title_el.get_attribute("href") if title_el else None
            company = company_el.inner_text().strip() if company_el else "Unknown"

            easy_apply = easy_apply_el is not None
            if easy_apply and link:
                jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "link": "https://www.linkedin.com" + link,
                    }
                )
        except TimeoutError:
            continue
        except Exception as e:
            print(f"⚠️ Error parsing job card: {e}")
            continue

    print(f"✅ Collected {len(jobs)} Easy Apply jobs.")
    return jobs
