"""Database models for linkedin-easy-apply
A simple dataclass representing a job application record.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class JobApplication:
    job_id: str
    title: str
    company: str
    applied_at: datetime
    status: str
    notes: Optional[str] = None


# Simple in-memory store for now
APPLICATIONS = []


def record_application(app: JobApplication) -> None:
    APPLICATIONS.append(app)
