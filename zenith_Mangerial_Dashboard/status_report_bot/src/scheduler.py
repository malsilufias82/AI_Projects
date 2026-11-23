"""
scheduler.py
------------
Sets up the scheduler with morning, evening, and weekly report jobs.
"""

import pytz
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import AppConfig
from logger import get_logger


class BotScheduler:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__, config.logs_folder, config.log_level)
        self.timezone = pytz.timezone(config.timezone)
        self.scheduler = BackgroundScheduler(timezone=self.timezone)

    def register_jobs(
        self,
        morning_job,
        evening_job,
        weekly_job,
    ):
        cfg = self.config.scheduler
        morning_hour, morning_minute = map(int, cfg.morning_time.split(":"))
        evening_hour, evening_minute = map(int, cfg.evening_time.split(":"))

        # Morning job: Mon-Fri at morning_time
        self.scheduler.add_job(
            morning_job,
            CronTrigger(
                day_of_week="mon-fri",
                hour=morning_hour,
                minute=morning_minute,
                timezone=self.timezone
            ),
            id="morning_report",
            replace_existing=True,
        )

        # Evening job: Mon-Fri at evening_time
        self.scheduler.add_job(
            evening_job,
            CronTrigger(
                day_of_week="mon-fri",
                hour=evening_hour,
                minute=evening_minute,
                timezone=self.timezone
            ),
            id="evening_report",
            replace_existing=True,
        )

        # Weekly job: Friday at evening_time
        self.scheduler.add_job(
            weekly_job,
            CronTrigger(
                day_of_week="fri",
                hour=evening_hour,
                minute=evening_minute,
                timezone=self.timezone
            ),
            id="weekly_report",
            replace_existing=True,
        )

        self.logger.info(
            f"Jobs registered: morning @ {cfg.morning_time}, evening @ {cfg.evening_time}, weekly @ Fri {cfg.evening_time} (tz: {self.config.timezone})"
        )

    def start(self) -> None:
        self.scheduler.start()
        self.logger.info("Scheduler started")

    def shutdown(self) -> None:
        self.scheduler.shutdown()
        self.logger.info("Scheduler stopped")


def get_previous_working_day(d: date, holidays: list[str] = None) -> date:
    if holidays is None:
        holidays = []
    one_day = timedelta(days=1)
    prev_day = d - one_day
    while True:
        # Check if it's a weekend
        if prev_day.weekday() >=5:
            prev_day -= one_day
            continue
        # Check if it's a holiday
        if prev_day.strftime("%Y-%m-%d") in holidays:
            prev_day -= one_day
            continue
        return prev_day


def get_week_days(d: date) -> list[date]:
    # Get Monday to Friday of the week containing d
    monday = d - timedelta(days=d.weekday())
    return [monday + timedelta(days=i) for i in range(5)]
