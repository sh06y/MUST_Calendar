# MUST Calendar

[English](README_EN.md) | [简体中文](README.md)

将澳门科技大学的学生课表与 WeMust OA 日程合并为一个 ICS 订阅，支持 iOS、Android、HarmonyOS、macOS 和 Windows 系统日历。

程序只登录一次 MUST 统一认证，然后分别读取：

- 学生课表：课程名称、教室、教师与上课时间
- WeMust OA 日程：活动、会议、假期及其他个人日程

OA 日程中重复提供的 `CLASS_TIMETABLE` 事件会被过滤，课程以学生课表接口为准。最终只生成 `output/[学号].ics`。

## 本地运行

1. Clone 仓库。
2. 在项目目录新建 `.env`：

    ```dotenv
    TERM_CODES=2502,2506
    USERNAME=你的学号
    PASSWORD=你的 WeMust 密码
    ALERT=30
    LOCALE=zh_MO
    CHROMEDRIVER_PATH=.venv/bin/chromedriver
    ```

3. 安装与本机 Chrome 主版本一致的 ChromeDriver：[Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/#stable)。如果 ChromeDriver 已在 `PATH` 中，可以省略 `CHROMEDRIVER_PATH`。
4. 建立虚拟环境并运行：

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python ./main.py
    ```

`TERM_CODES` 支持多个四位学期代码，以逗号分隔。程序会将这些学期的课表与当前日期前后各一年的 OA 日程合并。OA 日程会包含侧边筛选中所有可用事项类型，以及“我参与的”和“我管理的”事项；“忽略”事项不会导出。

## GitHub Actions 部署

1. Fork 仓库并启用 Actions。
2. 在 `Settings` → `Security` → `Secrets and variables` → `Actions` 中添加：
   - `USERNAME`：学号
   - `PASSWORD`：WeMust 密码
3. 在 [.github/workflows/python-app.yml](.github/workflows/python-app.yml) 中设置 `TERM_CODES`、`ALERT` 和 `LOCALE`。
4. 手动运行一次 `Update Calendar Everyday`，确认 `output/[学号].ics` 已生成。

订阅地址：

```text
https://raw.githubusercontent.com/你的GitHub账号/MUST_Calendar/refs/heads/main/output/[学号].ics
```

旧版按学期生成的 `output/[学号]_[学期代码].ics` 不再更新，需要在系统日历中改为新的统一订阅地址。

## 隐私提示

统一 ICS 会包含 OA 日程的标题、地点和备注。若仓库为公开仓库，这些内容也会公开；发布前请确认仓库和订阅地址的可见范围符合你的需求。

## 测试

```bash
python -m unittest discover -s tests -v
```

## TODO

- [x] 多学期
- [x] 多语言支持
- [x] 合并 WeMust OA 日程
- [ ] 考试日历

欢迎 PR 和 Issues。
