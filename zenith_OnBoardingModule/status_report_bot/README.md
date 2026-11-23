# Status Report Bot — Phase 1

Automates the weekly Friday status-report follow-up that was previously done
manually (as Shubhanshu does today): reads the team's Excel status report,
works out who hasn't submitted, posts grouped reminders to a Teams channel
tagging the right Team Lead, escalates at 5 PM and 6 PM, and produces
weekly/never-updated/last-to-submit reports.

**Phase 1 scope:** Excel + Teams + Scheduler only. No AI/OpenAI. Phase 2 will
add prediction of likely defaulters and daily (not just Friday) tracking —
the architecture below is built so that drops in cleanly later.

## How it works

| Time (Fri) | Action |
|---|---|
| 4:00 PM | Read Excel, find pending employees, group by Team Lead, post to Teams |
| every N min | Re-read Excel automatically; pending list updates as people submit (no restart needed) |
| 5:00 PM | Re-check, post reminder, tag the manager and requester, and (optionally) create one escalation Teams meeting per pending TL with requester + PM + manager as attendees |
| 6:00 PM | Repeat the 5 PM reminder if anyone is still pending |
| Once everyone submits | Posts a final "all reports completed" summary message |
| End of week (manual/cron) | Generates: (1) employees who never updated all week, with their TL, (2) employees who were last to submit, with their TL — both saved to `reports/`, and appends this week's never-updated list to a persistent `defaulters_history.json` for trend tracking |

### Important honesty note on "automated calls"
Microsoft Graph can create a Teams online meeting and add the manager, PM,
and the TL as attendees — the bot does this automatically at 5 PM and drops
the join link in the channel. It **cannot** make the meeting talk or hold a
conversation with the TL; a human still needs to join and deliver the
message, or the chat @mention has to do the prompting. If you want a true
voice prompt, that needs Azure Communication Services / a bot with calling
capability — out of scope for Phase 1 but the `teams_service.py` module is
the place it would plug in.

## Project structure

```
status_report_bot/
├── config/
│   └── config.json          # all non-secret configuration
├── src/
│   ├── main.py               # orchestrator / entry point
│   ├── config.py              # loads config.json + .env
│   ├── excel_reader.py        # reads Excel -> EmployeeRecord list
│   ├── report_checker.py      # pending/completed logic, defaulters history
│   ├── scheduler.py           # APScheduler cron jobs (4/5/6 PM Friday)
│   ├── teams_service.py       # Microsoft Graph: channel messages, meetings
│   ├── report_generator.py    # message formatting + report file output
│   └── logger.py              # shared rotating-file logger
├── logs/
├── reports/
├── data/
│   └── status_report.xlsx     # sample file (replace with the real one)
├── .env.example                # copy to .env and fill in secrets
├── requirements.txt
└── README.md
```

## Setup

1. `pip install -r requirements.txt`
2. `cp .env.example .env` and fill in your Azure AD app registration details
   (Tenant ID, Client ID, Client Secret), Teams Team/Channel IDs, and the
   manager / PM / requester emails.
3. Register an Azure AD app with **application** Graph permissions:
   `ChannelMessage.Send`, `OnlineMeetings.ReadWrite.All`, `User.Read.All`
   (admin consent required).
4. Point `config/config.json` → `excel_file` at your real weekly status
   report, and adjust column names if yours differ.
5. Run: `python src/main.py`

The bot runs continuously in the background; APScheduler fires the Friday
jobs automatically — no separate cron setup needed.

## Testing before Friday

Each module is independently testable. For example, to dry-run the Excel +
pending-grouping logic without touching Teams:

```python
from config import load_config
from excel_reader import ExcelReader
from report_checker import ReportChecker

cfg = load_config()
records = ExcelReader(cfg).read_employee_records()
snapshot = ReportChecker(cfg).evaluate(records)
print(snapshot.pending_by_tl)
```

## What's next (Phase 2)

`report_checker.py` already exposes `DefaultersTracker.get_repeat_defaulters()`,
which returns how many weeks each employee has shown up in the never-updated
list — this is the feature input an ML model would use to predict next
week's likely defaulters. Phase 2 would add a `predictor.py` module and move
the scheduler from "Friday only" to a daily check for at-risk employees,
without needing to change any of the Phase 1 modules.
