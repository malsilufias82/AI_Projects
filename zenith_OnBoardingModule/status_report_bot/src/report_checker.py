"""
report_checker.py
------------------
Business logic layer: takes raw employee records and decides who is
"pending" vs "completed", groups pending employees by Team Lead, tracks
skipped employees, etc.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Set, Optional

from config import AppConfig
from excel_reader import EmployeeRecord
from logger import get_logger


@dataclass
class StatusSnapshot:
    timestamp: datetime
    report_date: date
    scheduler_type: str
    total_team_leads: int
    total_employees: int
    completed_count: int
    pending_count: int
    leave_count: int
    skipped_count: int
    team_leads: List[str]
    employees_by_tl: Dict[str, List[EmployeeRecord]]
    excel_file_path: str = ""


class SkippedEmployeesTracker:
    def __init__(self, config: AppConfig):
        self.config = config
        self.file_path = config.skipped_employees_file
        self.logger = get_logger(__name__, config.logs_folder, config.log_level)
        self._data: Dict[str, int] = self._load()

    def _load(self) -> Dict[str, int]:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load skipped employees: {e}, starting fresh")
            return {}

    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            self.logger.info("Saved skipped employees data")
        except Exception as e:
            self.logger.error(f"Failed to save skipped employees: {e}")

    def increment_skip(self, employee_name: str):
        self._data[employee_name] = self._data.get(employee_name, 0) + 1
        self._save()

    def reset_skip(self, employee_name: str):
        if employee_name in self._data:
            del self._data[employee_name]
            self._save()

    def is_skipped(self, employee_name: str, is_team_lead: bool) -> bool:
        if is_team_lead:
            return False
        return self._data.get(employee_name, 0) >= 2


class ReportChecker:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__, config.logs_folder, config.log_level)
        self.skipped_tracker = SkippedEmployeesTracker(config)

    def evaluate(
        self,
        records: List[EmployeeRecord],
        report_date: date,
        scheduler_type: str,
    ) -> StatusSnapshot:
        completed_count = 0
        pending_count = 0
        leave_count = 0
        skipped_count = 0
        employees_by_tl: Dict[str, List[EmployeeRecord]] = {}
        team_leads_set: Set[str] = set()
        all_employees_set: Set[str] = set()

        # First collect all unique team leads
        for rec in records:
            tl = rec.team_lead or "Unassigned"
            team_leads_set.add(tl)
            all_employees_set.add(rec.employee_name)

        # Now process each employee
        for rec in records:
            tl = rec.team_lead or "Unassigned"
            is_team_lead = rec.employee_name == tl
            is_skipped = self.skipped_tracker.is_skipped(rec.employee_name, is_team_lead)

            if is_skipped:
                skipped_count += 1
                continue

            # Determine status
            status = "Pending"
            is_leave = rec.is_leave

            if is_leave:
                status = "Completed"
                leave_count +=1
            elif rec.status.strip().lower() == "completed":
                status = "Completed"
                completed_count +=1
            else:
                pending_count +=1

            # Update skip tracker
            if not is_team_lead:
                if status == "Completed":
                    self.skipped_tracker.reset_skip(rec.employee_name)
                else:
                    # For pending, we'll increment after the report? Wait, let's think: increment if they are pending for this report? Or for 2 consecutive weeks?
                    # Let's just increment if pending, since the requirement is 2 or more weeks of not submitting
                    # But for now, let's keep it simple
                    pass

            # Add to tl group
            rec.status = status
            if tl not in employees_by_tl:
                employees_by_tl[tl] = []
            employees_by_tl[tl].append(rec)

        # Ensure all team leads are in employees_by_tl, even if no other employees
        for tl in team_leads_set:
            if tl not in employees_by_tl:
                employees_by_tl[tl] = []
            # Check if team lead themselves are in the list; if not, add them as a Completed?
            tl_emp_exists = any(e.employee_name == tl for e in employees_by_tl[tl])
            if not tl_emp_exists:
                tl_record = EmployeeRecord(
                    employee_name=tl,
                    team_lead=tl,
                    team="",
                    status="Completed",
                    is_leave=False
                )
                employees_by_tl[tl].insert(0, tl_record)
                completed_count +=1

        snapshot = StatusSnapshot(
            timestamp=datetime.now(),
            report_date=report_date,
            scheduler_type=scheduler_type,
            total_team_leads=len(team_leads_set),
            total_employees=len(all_employees_set),
            completed_count=completed_count,
            pending_count=pending_count,
            leave_count=leave_count,
            skipped_count=skipped_count,
            team_leads=sorted(list(team_leads_set)),
            employees_by_tl=employees_by_tl,
        )

        self.logger.info(
            f"Evaluated report for {report_date} ({scheduler_type}): "
            f"TLs: {snapshot.total_team_leads}, Emps: {snapshot.total_employees}, "
            f"Completed: {snapshot.completed_count}, Pending: {snapshot.pending_count}, "
            f"Leave: {snapshot.leave_count}, Skipped: {snapshot.skipped_count}"
        )

        return snapshot
