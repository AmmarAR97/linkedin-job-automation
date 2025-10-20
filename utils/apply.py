import json
import os

import yaml
from dotenv import load_dotenv

from utils.humanize import random_sleep, wait_for_page_full_load

load_dotenv()


RESUME_PATH: str = os.getenv("RESUME_PATH", "")
PHONE: str = os.getenv("PHONE", "")
EMAIL: str = os.getenv("EMAIL", "")

with open("config.yaml") as f:
    config = yaml.safe_load(f).get("job_search", {})

YEARS_OF_EXPERIENCE = config.get("years_of_experience", 5)
EDUCATION_LEVEL = config.get("education_level", "Bachelor's Degree")
WORK_AUTHORIZATION = config.get("work_authorization", "Yes")
REQUIRE_SPONSORSHIP = config.get("require_sponsorship", "No")
WILLING_TO_RELOCATE = config.get("willing_to_relocate", "Yes")
NOTICE_PERIOD = config.get("notice_period", "15")
CURRENT_SALARY = config.get("current_salary", "1000000")
SALARY_EXPECTATION = config.get("salary_expectation", "1500000")
PREVIOUSLY_WORKED = config.get("previously_worked", "No")
REFERENCE_CHECK = config.get("reference_check", "Yes")
CERTIFICATIONS = config.get("certifications", "None")


answered_questions: set[str] = set()
unanswered_questions: set[str] = set()


def save_questions_data():
    questions_file = "questions.json"
    data = {
        "answered_questions": list(answered_questions),
        "unanswered_questions": list(unanswered_questions),
    }

    # If file exists, read and update values
    if os.path.exists(questions_file):
        with open(questions_file, "r") as f:
            existing_data = json.load(f)

        # Merge the lists (avoid duplicates)
        existing_data["answered_questions"] = list(
            set(existing_data.get("answered_questions", []))
            | set(data["answered_questions"])
        )
        existing_data["unanswered_questions"] = list(
            set(existing_data.get("unanswered_questions", []))
            | set(data["unanswered_questions"])
        )

        # Save updated data
        with open(questions_file, "w") as f:
            json.dump(existing_data, f, indent=4)

    else:
        # Create new file
        with open(questions_file, "w") as f:
            json.dump(data, f, indent=4)


def apply_for_jobs(page, jobs, limit=config.get("max_jobs", 10)):
    total = min(len(jobs), limit)
    print(f"➡️ Starting to apply to {total} jobs (out of {len(jobs)})")

    applied_count = 0
    for idx, job in enumerate(jobs[:limit], start=1):
        title = job.get("title", "Unknown")
        company = job.get("company", "Unknown")
        print(f"[{idx}/{total}] Applying to: {title} at {company}")

        try:
            success = apply_easy_apply_job(page, job)
            print(f"[{idx}/{total}] {'✅ Applied' if success else '❌ Skipped/Failed'}")
            if success:
                applied_count += 1
        except Exception as e:
            print(f"[{idx}/{total}] Exception while applying: {e}")

        random_sleep()

    print(f"➡️ Done. Applied to {applied_count}/{total} jobs.")

    save_questions_data()
    return applied_count


def apply_easy_apply_job(page, job):
    page.goto(job["link"])
    wait_for_page_full_load(page)
    random_sleep()

    try:
        easy_apply_btn = page.query_selector(
            ".jobs-apply-button--top-card #jobs-apply-button-id"
        )
        if not easy_apply_btn:
            print("❌ Easy Apply not available, skipping.")
            return False

        if easy_apply_btn:
            easy_apply_btn.click()
            print("Clicked the Easy Apply button inside the top card.")
        else:
            print("Easy Apply button in the top card not found.")

        random_sleep()

        # Wait for form modal to appear
        try:
            form_modal = page.wait_for_selector(
                "div.jobs-easy-apply-modal", timeout=7000
            )
        except Exception:
            print("⚠️ Form modal not found.")
            return False

        # Multi-step application handling
        max_steps = 10
        step_count = 0

        while step_count < max_steps:
            step_count += 1
            print(f"Processing step {step_count}...")

            # Fill phone if present
            phone_selectors = [
                "input[name*='phone']",
                "input[id*='phone']",
                "input[id*='phoneNumber']",
                "input[inputmode='tel']",
                "input[type='tel']",
                "input[aria-label*='phone']",
                "input[placeholder*='phone']",
                "input[inputmode='text'][id*='phone']",
            ]

            phone_input = None
            phone_input_selector = None
            for sel in phone_selectors:
                phone_input = form_modal.query_selector(sel)
                if phone_input:
                    phone_input_selector = sel
                    break

            random_sleep()

            if phone_input_selector and phone_input and PHONE:
                try:
                    phone_input.fill(PHONE)
                except Exception:
                    pass

            # Fill email if present
            email_input = form_modal.query_selector("input[name*='email']")
            if email_input:
                email_input.fill(EMAIL)

            # Handle file upload
            file_input = form_modal.query_selector("input[type='file']")
            if file_input:
                file_input.set_input_files(RESUME_PATH)

            # Handle text inputs and textareas (for experience, notice period, etc.)
            text_inputs = form_modal.query_selector_all(
                "input[type='text'], input[type='number'], textarea"
            )
            for inp in text_inputs:
                try:
                    label_text = get_label_for_input(page, inp)
                    answer = get_answer_for_question(label_text)
                    if answer and inp.is_visible():
                        answered_questions.add(label_text)
                        inp.fill(str(answer))
                        print(f"  Filled: {label_text} ... with: {answer}")
                    else:
                        unanswered_questions.add(label_text)
                except Exception as e:
                    print(f"  Error filling input: {e}")

            random_sleep()

            # Handle radio buttons
            radio_groups = form_modal.query_selector_all(
                "fieldset, div[role='radiogroup']"
            )
            for group in radio_groups:
                try:
                    label_text = get_label_for_input(page, group)
                    answers = ["Yes", "True"]
                    for answer in answers:
                        if select_radio_option(group, answer):
                            print(f"  Selected radio: {label_text}... with: {answer}")
                            break
                    else:
                        unanswered_questions.add(label_text)
                except Exception as e:
                    print(f"  Error handling radio group: {e}")

            random_sleep()

            # Handle dropdowns/select elements
            selects = form_modal.query_selector_all("select")
            for sel in selects:
                try:
                    label_text = get_label_for_input(page, sel)
                    answers = ["Yes", "True"]
                    for answer in answers:
                        if select_dropdown_option(sel, answer):
                            print(
                                f"  Selected dropdown: {label_text}... with: {answer}"
                            )
                            break
                    else:
                        unanswered_questions.add(label_text)
                except Exception as e:
                    print(f"  Error handling dropdown: {e}")

            random_sleep()

            # Detect submit button
            submit_btn = form_modal.query_selector(
                "button:has-text('Submit application')"
            )
            if submit_btn and submit_btn.is_visible():
                submit_btn.click()
                print(f"✅ Applied successfully to {job['title']}")
                random_sleep()
                return True
            else:
                # Check for review button
                review_btn = form_modal.query_selector("button:has-text('Review')")
                if review_btn and review_btn.is_visible():
                    review_btn.click()
                    random_sleep()
                else:
                    print("⚠️ Multi-step application")

                    # Check for "Next" button to continue multi-step form
                    next_btn = form_modal.query_selector(
                        "button:has-text('Next'), button[aria-label='Continue to next step']"
                    )
                    if next_btn and next_btn.is_visible():
                        next_btn.click()
                        print("Clicked Next button")
                        random_sleep()
                    else:
                        # No next button found, might be done or stuck
                        print("⚠️ No Next or Submit button found")
                        random_sleep()
                        break

        print("⚠️ Max steps reached or unable to complete application")
        return False

    except Exception as e:
        print(f"⚠️ Error applying to job: {e}")
        return False


def get_label_for_input(page, element):
    """Extract label text for an input element"""
    try:
        # Try to find associated label
        elem_id = element.get_attribute("id")
        if elem_id:
            label = page.query_selector(f"label[for='{elem_id}']")
            if label:
                return label.inner_text().strip()

        # Try parent label
        parent = element.evaluate("el => el.closest('label')")
        if parent:
            return element.evaluate("el => el.closest('label').innerText").strip()

        # Try aria-label
        aria_label = element.get_attribute("aria-label")
        if aria_label:
            return aria_label.strip()

        # Try placeholder
        placeholder = element.get_attribute("placeholder")
        if placeholder:
            return placeholder.strip()

        # Try fieldset legend (for radio groups)
        legend = element.query_selector("legend")
        if legend:
            return legend.inner_text().strip()

        return ""
    except Exception as e:
        print(f"⚠️ Error getting label for input: {e}")
        return ""


def get_answer_for_question(question_text):
    """Match question text to appropriate answer"""
    if not question_text:
        return None

    q_lower = question_text.lower()

    # Years of experience
    if any(
        kw in q_lower
        for kw in ["years of experience", "years experience", "how many years"]
    ):
        # if any(
        #     tech in q_lower
        #     for tech in ["python", "javascript", "java", "react", "node"]
        # ):
        #     return YEARS_OF_EXPERIENCE.get("specific_skill", "5")

        return YEARS_OF_EXPERIENCE

    # Education
    if any(
        kw in q_lower
        for kw in ["education", "degree", "qualification", "highest level"]
    ):
        return EDUCATION_LEVEL

    # Work authorization
    if any(
        kw in q_lower
        for kw in [
            "authorized to work",
            "legally authorized",
            "work authorization",
            "right to work",
        ]
    ):
        return WORK_AUTHORIZATION

    # Visa sponsorship
    if any(
        kw in q_lower
        for kw in ["visa sponsorship", "require sponsorship", "need sponsorship"]
    ):
        return REQUIRE_SPONSORSHIP

    # Location/onsite
    if any(
        kw in q_lower
        for kw in [
            "comfortable working",
            "willing to work",
            "work onsite",
            "relocate",
            "work in",
        ]
    ):
        return WILLING_TO_RELOCATE

    # Notice period
    if any(
        kw in q_lower
        for kw in [
            "notice period",
            "availability",
            "when can you start",
            "start date",
            "join",
        ]
    ):
        if "month" in q_lower:
            return str(round(int(NOTICE_PERIOD) / 30, 2))

        return NOTICE_PERIOD

    # Current Salary
    if any(
        kw in q_lower for kw in ["current fixed ctc", "current ctc", "expected salary"]
    ):
        return CURRENT_SALARY

    # Salary expectations
    if any(
        kw in q_lower
        for kw in [
            "salary",
            "compensation",
            "expected salary",
            "expected ctc",
            "salary expectation",
        ]
    ):
        return SALARY_EXPECTATION

    # Previous employment
    if any(
        kw in q_lower for kw in ["previously worked", "worked for", "former employee"]
    ):
        return PREVIOUSLY_WORKED

    # Reference check
    if any(kw in q_lower for kw in ["contact", "reference", "previous employer"]):
        return REFERENCE_CHECK

    # Certifications
    if any(kw in q_lower for kw in ["certification", "certified", "certificate"]):
        return CERTIFICATIONS

    return None


def select_radio_option(group_element, answer):
    """Select appropriate radio button based on answer"""
    try:
        answer_lower = str(answer).lower()

        # Map answers to common radio button patterns
        if answer_lower in ["yes", "true"]:
            radio = group_element.query_selector(
                "input[type='radio'][value='Yes'], input[type='radio'][value='yes'], input[type='radio'][value='true']"
            )
            if radio and radio.is_visible():
                try:
                    radio.click()
                except Exception:
                    radio.click(force=True)
                return True

        if answer_lower in ["no", "false"]:
            radio = group_element.query_selector(
                "input[type='radio'][value='No'], input[type='radio'][value='no'], input[type='radio'][value='false']"
            )
            if radio and radio.is_visible():
                try:
                    radio.click()
                except Exception:
                    radio.click(force=True)
                return True

        # Try to find radio with matching label
        labels = group_element.query_selector_all("label")
        for label in labels:
            if answer_lower in label.inner_text().lower():
                radio_id = label.get_attribute("for")
                if radio_id:
                    radio = group_element.query_selector(
                        f"input[type='radio']#{radio_id}"
                    )
                    if radio and radio.is_visible():
                        try:
                            radio.click()
                        except Exception:
                            radio.click(force=True)
                        return True
        return False
    except Exception as e:
        print(f"Error selecting radio: {e}")


def select_dropdown_option(select_element, answer):
    """Select appropriate dropdown option based on answer"""
    try:
        answer_str = str(answer)
        options = select_element.query_selector_all("option")
        for option in options:
            option_text = option.inner_text().strip()
            if (
                answer_str.lower() in option_text.lower()
                or option_text.lower() in answer_str.lower()
            ):
                select_element.select_option(value=option.get_attribute("value"))
                return True
        return False
    except Exception as e:
        print(f"Error selecting dropdown: {e}")
