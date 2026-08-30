from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

from calendar_exporter import UnifiedCalendarExporter
from login import Login
from sources import ClassTimetableSource, OAScheduleSource


CLASS_TIMETABLE_SITE_URL = (
    "https://classtimetable-coes-wmweb.must.edu.mo/my-class-timetable-student"
)
OA_SCHEDULE_SITE_URL = "https://oa-schedule-new-wmweb.must.edu.mo/"
SUPPORTED_LOCALES = {"zh_MO", "en_US"}
CALENDAR_RANGE_DAYS = 365


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class Configuration:
    term_codes: tuple[str, ...]
    username: str
    password: str
    alert_minutes: int
    locale: str

    @classmethod
    def from_environment(cls) -> "Configuration":
        term_codes = parse_term_codes(os.environ.get("TERM_CODES", ""))
        username = os.environ.get("USERNAME", "").strip()
        password = os.environ.get("PASSWORD", "")
        locale = os.environ.get("LOCALE", "zh_MO").strip() or "zh_MO"

        if not username or not password:
            raise ConfigurationError("USERNAME and PASSWORD are required")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", username):
            raise ConfigurationError("USERNAME cannot be used as a calendar filename")
        if locale not in SUPPORTED_LOCALES:
            raise ConfigurationError("LOCALE must be zh_MO or en_US")

        try:
            alert_minutes = int(os.environ.get("ALERT", "30"))
        except ValueError as error:
            raise ConfigurationError("ALERT must be an integer") from error
        if alert_minutes < 0:
            raise ConfigurationError("ALERT must not be negative")

        return cls(
            term_codes=term_codes,
            username=username,
            password=password,
            alert_minutes=alert_minutes,
            locale=locale,
        )


def parse_term_codes(value: str) -> tuple[str, ...]:
    term_codes = tuple(part.strip() for part in value.split(",") if part.strip())
    if not term_codes:
        raise ConfigurationError("TERM_CODES must contain at least one term code")
    for term_code in term_codes:
        if len(term_code) != 4 or not term_code.isdigit():
            raise ConfigurationError(f"Invalid term code: {term_code}")
    if len(set(term_codes)) != len(term_codes):
        raise ConfigurationError("TERM_CODES must not contain duplicate term codes")
    return term_codes


def run(configuration: Configuration) -> Path:
    login = Login(configuration.username, configuration.password)
    try:
        class_cookie = login.get_site_cookie(
            CLASS_TIMETABLE_SITE_URL,
            "wm.class-timetable.sid",
        )
        oa_cookie = login.get_site_cookie(
            OA_SCHEDULE_SITE_URL,
            "wm.schedule.sid",
        )
    finally:
        login.close()

    today = date.today()
    start_date = today - timedelta(days=CALENDAR_RANGE_DAYS)
    end_date = today + timedelta(days=CALENDAR_RANGE_DAYS)

    class_events = ClassTimetableSource(
        class_cookie,
        locale=configuration.locale,
    ).fetch(configuration.term_codes, start_date, end_date)
    print(f"Success: {len(class_events)} class timetable events found")

    oa_events = OAScheduleSource(
        oa_cookie,
        locale=configuration.locale,
    ).fetch(start_date, end_date)
    print(f"Success: {len(oa_events)} OA schedule events found")

    output_path = UnifiedCalendarExporter(configuration.username).export(
        [*class_events, *oa_events],
        trigger_minutes=configuration.alert_minutes,
    )
    print(f"Success: {output_path} created")
    return output_path


def main() -> None:
    load_dotenv()
    run(Configuration.from_environment())


if __name__ == "__main__":
    main()
