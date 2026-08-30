import os
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from calendar_exporter import CalendarEvent
from main import Configuration, ConfigurationError, parse_term_codes, run


MACAU_TIMEZONE = ZoneInfo("Asia/Macau")


class ConfigurationTests(unittest.TestCase):
    def test_reads_unified_calendar_configuration(self):
        environment = {
            "TERM": "dumb",
            "TERM_CODES": "2609, 2702",
            "USERNAME": "student",
            "PASSWORD": "password",
        }
        with patch.dict(os.environ, environment, clear=True):
            configuration = Configuration.from_environment()

        self.assertEqual(configuration.term_codes, ("2609", "2702"))
        self.assertEqual(configuration.alert_minutes, 30)
        self.assertEqual(configuration.locale, "zh_MO")

    def test_rejects_duplicate_or_invalid_term_codes(self):
        with self.assertRaises(ConfigurationError):
            parse_term_codes("2609,2609")
        with self.assertRaises(ConfigurationError):
            parse_term_codes("2026-fall")


class MainFlowTests(unittest.TestCase):
    def event(self, source, source_id):
        start = datetime(2026, 9, 1, 9, 0, tzinfo=MACAU_TIMEZONE)
        return CalendarEvent(
            source=source,
            source_id=source_id,
            summary="Event",
            start=start,
            end=start + timedelta(hours=1),
        )

    @patch("main.UnifiedCalendarExporter")
    @patch("main.OAScheduleSource")
    @patch("main.ClassTimetableSource")
    @patch("main.Login")
    def test_one_login_collects_both_sources_into_one_export(
        self,
        login_type,
        class_source_type,
        oa_source_type,
        exporter_type,
    ):
        login = login_type.return_value
        login.get_site_cookie.side_effect = ["class-cookie", "oa-cookie"]
        class_event = self.event("class-timetable", "2609:1001")
        oa_event = self.event("oa-schedule", "9001")
        class_source_type.return_value.fetch.return_value = [class_event]
        oa_source_type.return_value.fetch.return_value = [oa_event]
        exporter_type.return_value.export.return_value = Path("output/student.ics")
        configuration = Configuration(
            term_codes=("2609", "2702"),
            username="student",
            password="password",
            alert_minutes=15,
            locale="zh_MO",
        )

        output_path = run(configuration)

        self.assertEqual(output_path, Path("output/student.ics"))
        self.assertEqual(login.get_site_cookie.call_count, 2)
        login.close.assert_called_once_with()
        class_source_type.assert_called_once_with("class-cookie", locale="zh_MO")
        oa_source_type.assert_called_once_with("oa-cookie", locale="zh_MO")
        exporter_type.assert_called_once_with("student")
        exporter_type.return_value.export.assert_called_once_with(
            [class_event, oa_event],
            trigger_minutes=15,
        )


if __name__ == "__main__":
    unittest.main()
