import hashlib
import unittest
from datetime import date, timedelta

from sources import (
    ClassTimetableSource,
    OAScheduleSource,
    SourceDataError,
    build_signature,
    iter_date_windows,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payloads):
        self.responses = [FakeResponse(payload) for payload in payloads]
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


class ClassTimetableSourceTests(unittest.TestCase):
    def test_normalises_lessons_and_skips_cancelled_records(self):
        session = FakeSession(
            [
                {
                    "model": {
                        "lesson": [
                            {
                                "id": 1001,
                                "status": "NORMAL",
                                "courseName": "測試課程",
                                "roomChnDesc": "A101",
                                "teacherName": "測試教師",
                                "lessonDate": "2026-09-01",
                                "lessonStartTime": "09:00",
                                "lessonEndTime": "10:00",
                            },
                            {
                                "id": 2001,
                                "status": "CANCEL",
                                "lessonDate": "2026-09-01",
                                "lessonStartTime": "11:00",
                                "lessonEndTime": "12:00",
                            },
                        ]
                    }
                }
            ]
        )
        source = ClassTimetableSource("cookie", session=session)

        events = source.fetch(
            ["2609"],
            date(2026, 1, 1),
            date(2026, 12, 31),
        )

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.identity, "class-timetable:2609:1001")
        self.assertEqual(event.summary, "測試課程")
        self.assertEqual(event.location, "A101")
        self.assertEqual(event.start.utcoffset(), timedelta(hours=8))
        _, request = session.calls[0]
        self.assertEqual(request["params"]["termCode"], "2609")
        self.assertIn("wm.class-timetable.sid=cookie", request["headers"]["Cookie"])


class OAScheduleSourceTests(unittest.TestCase):
    SERVICE_TYPES_PAYLOAD = {
        "success": True,
        "model": [
            {"code": "25", "name": "Leave"},
            {"code": "152", "name": "Activity"},
            {"code": "119", "name": "Schedule"},
            {"code": "193", "name": "Bookshop"},
            {"code": "461", "name": "Staff Training"},
        ],
    }

    def event(self, event_id, **overrides):
        value = {
            "id": event_id,
            "title": "OA Event",
            "address": "N101",
            "remark": "First<br>Second",
            "eventType": "ACTIVITY",
            "eventStartDate": "2026-08-30",
            "eventEndDate": "2026-08-30",
            "eventStartTime": "14:00",
            "eventEndTime": "15:00",
            "isIgnore": False,
        }
        value.update(overrides)
        return value

    def test_signs_request_and_normalises_active_non_class_events(self):
        active = self.event(9001)
        all_day = self.event(
            9002,
            title="Holiday",
            eventType="HOLIDAY",
            eventStartDate="2026-08-31",
            eventEndDate="2026-09-01",
            eventStartTime=None,
            eventEndTime=None,
        )
        session = FakeSession(
            [
                self.SERVICE_TYPES_PAYLOAD,
                {
                    "success": True,
                    "model": [
                        {
                            "date": "2026-08-30",
                            "events": [
                                active,
                                self.event(9003, isIgnore=True),
                                self.event(9004, eventType="CLASS_TIMETABLE"),
                            ],
                        },
                        {
                            "date": "2026-08-31",
                            "events": [active, all_day],
                        },
                    ],
                }
            ]
        )
        source = OAScheduleSource(
            "cookie",
            session=session,
            nonce_factory=lambda: "fixed-nonce",
        )

        events = source.fetch(date(2026, 8, 1), date(2026, 8, 31))

        self.assertEqual({event.source_id for event in events}, {"9001", "9002"})
        timed = next(event for event in events if event.source_id == "9001")
        self.assertEqual(timed.description, "First\nSecond")
        self.assertEqual(timed.start.utcoffset(), timedelta(hours=8))
        holiday = next(event for event in events if event.source_id == "9002")
        self.assertEqual(holiday.start, date(2026, 8, 31))
        self.assertEqual(holiday.end, date(2026, 9, 2))

        _, service_request = session.calls[0]
        self.assertEqual(service_request["params"]["key"], "SERVICE")
        self.assertEqual(
            service_request["params"]["serviceCode"],
            "S-WM-SCHEDULE-NEW",
        )

        _, request = session.calls[1]
        params = request["params"]
        signature_input = (
            "dataSource=1"
            "endTime=2026-08-31"
            "isIgnore=0"
            "isJoin=1"
            "isManage=1"
            "lang=zh_MO"
            "nonce=fixed-nonce"
            "serviceIds=25"
            "startTime=2026-08-01"
            "wm_oa_schedule_new"
        )
        expected_signature = hashlib.md5(signature_input.encode()).hexdigest()
        self.assertEqual(params["signature"], expected_signature)
        self.assertEqual(params["serviceIds"], ["25", "152", "119", "193", "461"])
        self.assertIn("wm.schedule.sid=cookie", request["headers"]["Cookie"])

    def test_date_range_is_split_into_at_most_three_month_windows(self):
        windows = list(iter_date_windows(date(2026, 1, 31), date(2026, 8, 1)))

        self.assertEqual(windows[0], (date(2026, 1, 31), date(2026, 4, 29)))
        self.assertEqual(windows[-1][1], date(2026, 8, 1))
        for start, end in windows:
            self.assertLessEqual((end - start).days, 92)
        for previous, current in zip(windows, windows[1:]):
            self.assertEqual(previous[1] + timedelta(days=1), current[0])

    def test_null_model_is_treated_as_an_empty_date_window(self):
        session = FakeSession(
            [self.SERVICE_TYPES_PAYLOAD, {"success": True, "model": None}]
        )
        source = OAScheduleSource(
            "cookie",
            session=session,
            nonce_factory=lambda: "fixed-nonce",
        )

        events = source.fetch(date(2026, 8, 1), date(2026, 8, 31))

        self.assertEqual(events, [])

    def test_requires_at_least_one_available_service_type(self):
        session = FakeSession([{"success": True, "model": []}])
        source = OAScheduleSource(
            "cookie",
            session=session,
            nonce_factory=lambda: "fixed-nonce",
        )

        with self.assertRaises(SourceDataError):
            source.fetch(date(2026, 8, 1), date(2026, 8, 31))

    def test_signature_uses_first_value_for_repeated_query_parameters(self):
        signature = build_signature(
            {
                "z": None,
                "list": ["first", "second"],
                "enabled": 1,
            },
            "salt",
        )
        expected = hashlib.md5("enabled=1list=firstsalt".encode()).hexdigest()

        self.assertEqual(signature, expected)


if __name__ == "__main__":
    unittest.main()
