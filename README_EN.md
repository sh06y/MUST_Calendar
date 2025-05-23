# MUST_Calendar 

[English](README_EN.md) | [简体中文](README.md)

Import University of Macau of Science and Technology (MUST) wemust course schedule into system calendar (iOS, Android, HarmonyOS, Mac OS, Windows) via ics file.

## Local Deployment

1. Clone the repository
2. Create a new ``config.py`` in the directory
    ```python
    termCode='2502,2506' # Term code, separated by commas
    username='Your student ID'
    password='Your password'
    ```
3. Install chrome driver (if not installed) [https://googlechromelabs.github.io/chrome-for-testing/#stable](https://googlechromelabs.github.io/chrome-for-testing/#stable)
3. Install dependencies and run
    ```
    pip install -r requirements.txt
    python ./main.py
    ```

## GitHub Action Deployment

1. Fork the repository
2. `Actions`-Agree to Workflow
3. `Settings` - `Security` - `Secrets and variables` - `Actions` - `New repository secret`
4. Fill `USERNAME` in name field, `Secret` with your student ID
5. Similarly, add another secret named `PASSWORD` with your Wemust password as `Value`
6. Modify [.github/workflows/python-app.yml](.github/workflows/python-app.yml), set term code at line `13`; uncomment line `27` to enable scheduled runs.

### Usage (iOS as example)

1. Open Calendar app
2. Calendar-Add Calendar-Add Subscription Calendar
3. Enter <https://raw.githubusercontent.com/yourGitHubAccount/MUST_Calendar/refs/heads/main/output/[StudentID]_[TermCode].ics>

The calendar will update daily at midnight, which can be modified in ```.github/workflows/python-app.yml```.

## TODO

- [x] Multiple terms
- [x] Multi-language support


PRs and Issues are welcome!