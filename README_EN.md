# MUST Calendar

[English](README_EN.md) | [简体中文](README.md)

Merge the Macau University of Science and Technology student timetable and WeMust OA schedule into one ICS subscription for iOS, Android, HarmonyOS, macOS, and Windows calendars.

The program signs in to MUST CAS once and then reads:

- Student timetable: course names, rooms, teachers, and lesson times
- WeMust OA schedule: activities, meetings, holidays, and other personal events

`CLASS_TIMETABLE` events duplicated by OA are excluded, so course data remains authoritative from the student timetable API. The only generated file is `output/[StudentID].ics`.

## Local setup

1. Clone the repository.
2. Create `.env` in the project directory:

    ```dotenv
    TERM_CODES=2502,2506
    USERNAME=Your student ID
    PASSWORD=Your WeMust password
    ALERT=30
    LOCALE=en_US
    CHROMEDRIVER_PATH=.venv/bin/chromedriver
    ```

3. Install a ChromeDriver whose major version matches Chrome: [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/#stable). Omit `CHROMEDRIVER_PATH` if ChromeDriver is already in `PATH`.
4. Create a virtual environment and run the exporter:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python ./main.py
    ```

`TERM_CODES` accepts comma-separated four-digit term codes. Lessons from those terms are merged with OA events in a rolling one-year window before and after the current date. OA events include every available event type from the sidebar filter plus both joined and managed events; ignored events are excluded.

## GitHub Actions deployment

1. Fork the repository and enable Actions.
2. Add these repository secrets under `Settings` → `Security` → `Secrets and variables` → `Actions`:
   - `USERNAME`: student ID
   - `PASSWORD`: WeMust password
3. Set `TERM_CODES`, `ALERT`, and `LOCALE` in [.github/workflows/python-app.yml](.github/workflows/python-app.yml).
4. Run `Update Calendar Everyday` once and verify that `output/[StudentID].ics` is created.

Subscription URL:

```text
https://raw.githubusercontent.com/yourGitHubAccount/MUST_Calendar/refs/heads/main/output/[StudentID].ics
```

The old per-term files at `output/[StudentID]_[TermCode].ics` are no longer updated. Replace them with the unified subscription URL in your calendar application.

## Privacy

The unified ICS contains OA event titles, locations, and remarks. If the repository is public, that information is public as well. Confirm that the repository and subscription URL visibility are appropriate before publishing it.

## Tests

```bash
python -m unittest discover -s tests -v
```

## TODO

- [x] Multiple terms
- [x] Multiple languages
- [x] WeMust OA schedule integration
- [ ] Exam calendar

PRs and Issues are welcome.
