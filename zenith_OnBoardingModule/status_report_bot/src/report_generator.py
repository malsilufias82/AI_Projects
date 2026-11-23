"""
report_generator.py
--------------------
Builds human-readable Teams message bodies and writes JSON/CSV report
files into the configured reports folder: pending reports, final
completion reports, never-updated lists, and last-to-submit lists.
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, List

from config import AppConfig
from excel_reader import EmployeeRecord
from logger import get_logger
from report_checker import StatusSnapshot


class ReportGenerator:
    """Formats Teams messages and persists report files to disk."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__, config.logs_folder, config.log_level)

    # ------------------------------------------------------------------
    # Teams message formatting
    # ------------------------------------------------------------------
    def format_pending_message(self, snapshot: StatusSnapshot) -> str:
        """Builds an HTML message like: 'TL Rahul: Amit, Neha have not submitted...'"""
        if not snapshot.pending_by_tl:
            return "<p>All employees have submitted their status report. ✅</p>"

        lines = ["<p><b>Pending Weekly Status Reports</b></p>", "<ul>"]
        for tl, employees in snapshot.pending_by_tl.items():
            names = ", ".join(e.employee_name for e in employees)
            verb = "have" if len(employees) > 1 else "has"
            lines.append(f"<li><b>TL {tl}</b>: {names} {verb} not submitted their status report.</li>")
        lines.append("</ul>")
        return "\n".join(lines)

    def format_final_message(self, snapshot: StatusSnapshot, total_employees: int) -> str:
        return (
            "<p><b>✅ Weekly Status Report - All Submitted</b></p>"
            f"<p>Total Employees: {total_employees}<br>"
            f"Completed: {len(snapshot.completed)}<br>"
            f"Pending: {len(snapshot.pending)}<br>"
            f"Completion Time: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>"
        )

    # ------------------------------------------------------------------
    # File persistence
    # ------------------------------------------------------------------
    def save_pending_report(self, snapshot: StatusSnapshot, label: str) -> str:
        """Saves the current pending-by-TL breakdown as JSON. Returns the file path."""
        path = self._report_path(f"pending_report_{label}.json")
        data = {
            tl: [self._record_to_dict(e) for e in employees]
            for tl, employees in snapshot.pending_by_tl.items()
        }
        self._write_json(path, {"timestamp": snapshot.timestamp.isoformat(), "pending_by_tl": data})
        return path

    def save_final_report(self, snapshot: StatusSnapshot, total_employees: int) -> str:
        path = self._report_path("final_report.json")
        data = {
            "total_employees": total_employees,
            "completed_employees": len(snapshot.completed),
            "pending_employees": len(snapshot.pending),
            "completion_time": snapshot.timestamp.isoformat(),
        }
        self._write_json(path, data)
        return path

    def save_never_updated_report(self, never_updated: List[EmployeeRecord]) -> str:
        path = self._report_path("never_updated.csv")
        self._write_csv(
            path,
            headers=["Employee Name", "Employee ID", "Team Lead", "Team"],
            rows=[[e.employee_name, e.employee_id, e.team_lead, e.team] for e in never_updated],
        )
        return path

    def save_last_to_submit_report(self, last_to_submit: List[Dict[str, str]], lookup_by_id: Dict[str, EmployeeRecord]) -> str:
        path = self._report_path("last_to_submit.csv")
        rows = []
        for entry in last_to_submit:
            rec = lookup_by_id.get(entry["employee_id"])
            rows.append([
                rec.employee_name if rec else entry["employee_id"],
                entry["employee_id"],
                rec.team_lead if rec else "",
                entry["completed_at"],
            ])
        self._write_csv(
            path,
            headers=["Employee Name", "Employee ID", "Team Lead", "Completed At"],
            rows=rows,
        )
        return path

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _report_path(self, filename: str) -> str:
        os.makedirs(self.config.reports_folder, exist_ok=True)
        return os.path.join(self.config.reports_folder, filename)

    def _write_json(self, path: str, data: Dict) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Report written: {path}")
        except OSError as exc:
            self.logger.error(f"Failed to write report '{path}': {exc}")

    def _write_csv(self, path: str, headers: List[str], rows: List[List[str]]) -> None:
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            self.logger.info(f"Report written: {path}")
        except OSError as exc:
            self.logger.error(f"Failed to write report '{path}': {exc}")

    @staticmethod
    def _record_to_dict(rec: EmployeeRecord) -> Dict:
        return {
            "employee_name": rec.employee_name,
            "employee_id": rec.employee_id,
            "team": rec.team,
            "status": rec.status,
        }
