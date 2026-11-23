"""
main.py
-------
Entry point for the automated status report scheduler.
"""

import time
from datetime import datetime, date, timedelta

from config import AppConfig, load_config
from excel_reader import ExcelReader
from logger import get_logger
from report_checker import ReportChecker, StatusSnapshot
from excel_report_generator import ExcelReportGenerator, DailyReportData, WeeklyReportData
from scheduler import BotScheduler, get_previous_working_day, get_week_days


class StatusReportBot:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__, config.logs_folder, config.log_level)

        self.excel_reader = ExcelReader(config)
        self.report_checker = ReportChecker(config)
        self.excel_generator = ExcelReportGenerator(config)

    def generate_daily_report(self, report_date: date, scheduler_type: str) -> StatusSnapshot:
        self.logger.info(f"Generating {scheduler_type} report for {report_date}")
        records, sheet_info = self.excel_reader.read_employee_records(report_date)
        snapshot = self.report_checker.evaluate(records, report_date, scheduler_type)

        daily_data = DailyReportData(
            report_date=snapshot.report_date,
            scheduler_type=snapshot.scheduler_type,
            team_leads=snapshot.team_leads,
            employees_by_tl=snapshot.employees_by_tl,
            completed_count=snapshot.completed_count,
            pending_count=snapshot.pending_count,
            leave_count=snapshot.leave_count,
            skipped_count=snapshot.skipped_count,
            sheet_info=sheet_info
        )

        excel_path = self.excel_generator.generate_daily_report(daily_data)
        snapshot.excel_file_path = excel_path

        self.logger.info(
            f"Daily report generated: {excel_path}"
        )
        return snapshot

    def generate_weekly_report(self, week_start: date) -> None:
        self.logger.info(f"Generating weekly report for week starting {week_start}")
        days = get_week_days(week_start)
        
        daily_status = {}
        all_records = []
        team_leads = set()
        employees_by_tl = {}
        all_sheet_info = {}
        
        for day in days:
            records, sheet_info = self.excel_reader.read_employee_records(day)
            # Merge sheet info
            for team_name, sheet_names in sheet_info.items():
                if team_name not in all_sheet_info:
                    all_sheet_info[team_name] = []
                for sheet_name in sheet_names:
                    if sheet_name not in all_sheet_info[team_name]:
                        all_sheet_info[team_name].append(sheet_name)
            
            if not all_records:
                all_records = records
                # Collect team leads and employees by tl from first day
                for rec in records:
                    tl = rec.team_lead or "Unassigned"
                    team_leads.add(tl)
                    if tl not in employees_by_tl:
                        employees_by_tl[tl] = []
                    # Check if employee already in tl's list
                    if not any(e.employee_name == rec.employee_name for e in employees_by_tl[tl]):
                        employees_by_tl[tl].append(rec)
        
        # Now collect status per day per employee
        for day in days:
            records, _ = self.excel_reader.read_employee_records(day)
            day_str = day.strftime("%Y-%m-%d")
            for rec in records:
                if rec.employee_name not in daily_status:
                    daily_status[rec.employee_name] = {}
                status = rec.status
                if rec.is_leave:
                    status = "On Leave"
                daily_status[rec.employee_name][day_str] = status
        
        # Calculate stats
        total_team_leads = len(team_leads)
        total_employees = len(all_records)
        
        # Generate weekly data
        weekly_data = WeeklyReportData(
            week_start_date=week_start,
            days=days,
            team_leads=sorted(list(team_leads)),
            employees_by_tl=employees_by_tl,
            daily_status=daily_status,
            stats={
                "total_team_leads": total_team_leads,
                "total_employees": total_employees,
                "completed_count": 0,
                "pending_count": 0,
                "leave_count": 0,
                "skipped_count": 0,
                "completion_percent": 0,
            },
            sheet_info=all_sheet_info
        )
        
        excel_path = self.excel_generator.generate_weekly_report(weekly_data)
        self.logger.info(f"Weekly report generated: {excel_path}")

    def on_morning_job(self) -> None:
        today = date.today()
        report_date = get_previous_working_day(today, self.config.scheduler.holidays)
        self.logger.info(f"Morning job triggered for {today}, generating report for {report_date}")
        self.generate_daily_report(report_date, "Morning")

    def on_evening_job(self) -> None:
        today = date.today()
        # Check if today is a working day (not weekend or holiday)
        if today.weekday() >=5:
            self.logger.info(f"Today {today} is a weekend, skipping evening job")
            return
        if today.strftime("%Y-%m-%d") in self.config.scheduler.holidays:
            self.logger.info(f"Today {today} is a holiday, skipping evening job")
            return
        
        self.logger.info(f"Evening job triggered for {today}")
        self.generate_daily_report(today, "Evening")

    def on_weekly_job(self) -> None:
        today = date.today()
        # Get week starting Monday
        week_start = today - timedelta(days=today.weekday())
        self.logger.info(f"Weekly job triggered, generating report for week starting {week_start}")
        self.generate_weekly_report(week_start)


def main() -> None:
    config = load_config()
    logger = get_logger(__name__, config.logs_folder, config.log_level)
    logger.info(f"Starting Status Report Scheduler (environment: {config.environment})")

    bot = StatusReportBot(config)
    scheduler = BotScheduler(config)

    scheduler.register_jobs(
        morning_job=bot.on_morning_job,
        evening_job=bot.on_evening_job,
        weekly_job=bot.on_weekly_job,
    )
    scheduler.start()

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown signal received, stopping scheduler")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
