import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar

from calendar_exporter import CalendarEvent, UnifiedCalendarExporter


MACAU_TIMEZONE = ZoneInfo("Asia/Macau")
GENERATED_AT = datetime(2026, 8, 31, 0, 0, tzinfo=timezone.utc)


class UnifiedCalendarExporterTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temporary_directory.name)
        self.exporter = UnifiedCalendarExporter("student", self.output_dir)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def timed_event(
        self,
        source_id: str,
        source: str = "class-timetable",
        day: int = 1,
        hour: int = 9,
    ) -> CalendarEvent:
        start = datetime(2026, 9, day, hour, 0, tzinfo=MACAU_TIMEZONE)
        return CalendarEvent(
            source=source,
            source_id=source_id,
            summary=f"Event {source_id}",
            start=start,
            end=start + timedelta(hours=1),
            location="A101",
            description="Description",
        )

    def read_calendar(self, events):
        output_path = self.exporter.export(
            events,
            trigger_minutes=30,
            generated_at=GENERATED_AT,
        )
        return output_path, Calendar.from_ical(output_path.read_bytes())

    @staticmethod
    def events(calendar):
        return [
            component for component in calendar.walk() if component.name == "VEVENT"
        ]

    def test_exports_one_unified_calendar_with_both_sources(self):
        output_path, calendar = self.read_calendar(
            [
                self.timed_event("2609:1001"),
                self.timed_event("9001", source="oa-schedule", hour=14),
            ]
        )

        self.assertEqual(output_path, self.output_dir / "student.ics")
        self.assertEqual(str(calendar["VERSION"]), "2.0")
        self.assertEqual(str(calendar["PRODID"]), "MUST Calendar")
        self.assertEqual(len(self.events(calendar)), 2)

    def test_same_source_identity_keeps_uid_when_schedule_changes(self):
        _, before = self.read_calendar([self.timed_event("2609:1001")])
        _, after = self.read_calendar(
            [self.timed_event("2609:1001", day=3, hour=14)]
        )

        before_event = self.events(before)[0]
        after_event = self.events(after)[0]
        self.assertEqual(str(before_event["UID"]), str(after_event["UID"]))
        self.assertNotEqual(
            before_event.decoded("DTSTART"),
            after_event.decoded("DTSTART"),
        )

    def test_removed_event_disappears_while_other_uid_stays_stable(self):
        _, before = self.read_calendar(
            [self.timed_event("2609:1001"), self.timed_event("2609:2001")]
        )
        _, after = self.read_calendar([self.timed_event("2609:2001")])

        before_uids = {str(event["UID"]) for event in self.events(before)}
        after_uids = {str(event["UID"]) for event in self.events(after)}
        self.assertEqual(len(after_uids), 1)
        self.assertTrue(after_uids.issubset(before_uids))

    def test_same_raw_id_from_different_sources_has_distinct_uid(self):
        _, calendar = self.read_calendar(
            [
                self.timed_event("1001", source="class-timetable"),
                self.timed_event("1001", source="oa-schedule"),
            ]
        )

        uids = {str(event["UID"]) for event in self.events(calendar)}
        self.assertEqual(len(uids), 2)

    def test_timed_event_is_written_in_utc_with_alarm(self):
        _, calendar = self.read_calendar([self.timed_event("2609:1001")])
        event = self.events(calendar)[0]

        self.assertEqual(event.decoded("DTSTART").utcoffset(), timedelta(0))
        self.assertEqual(event.decoded("DTSTAMP"), GENERATED_AT)
        alarms = [
            component
            for component in event.subcomponents
            if component.name == "VALARM"
        ]
        self.assertEqual(len(alarms), 1)
        self.assertEqual(alarms[0].decoded("TRIGGER"), timedelta(minutes=-30))

    def test_all_day_event_uses_exclusive_end_date_without_alarm(self):
        all_day = CalendarEvent(
            source="oa-schedule",
            source_id="9002",
            summary="Holiday",
            start=date(2026, 10, 1),
            end=date(2026, 10, 3),
        )
        _, calendar = self.read_calendar([all_day])
        event = self.events(calendar)[0]

        self.assertEqual(event.decoded("DTSTART"), date(2026, 10, 1))
        self.assertEqual(event.decoded("DTEND"), date(2026, 10, 3))
        self.assertEqual(event.subcomponents, [])

    def test_conflicting_duplicate_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Conflicting calendar events"):
            self.exporter.build(
                [
                    self.timed_event("2609:1001", hour=9),
                    self.timed_event("2609:1001", hour=10),
                ]
            )


if __name__ == "__main__":
    unittest.main()
