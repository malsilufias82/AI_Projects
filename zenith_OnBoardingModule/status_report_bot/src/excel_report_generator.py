"""
excel_report_generator.py
-------------------------
Generates well-formatted Excel reports with styling, conditional formatting, etc.
"""

import os
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

from config import AppConfig
from excel_reader import EmployeeRecord
from logger import get_logger


@dataclass
class DailyReportData:
    report_date: date
    scheduler_type: str  # "Morning", "Evening", "Weekly"
    team_leads: List[str]
    employees_by_tl: Dict[str, List[EmployeeRecord]]
    completed_count: int
    pending_count: int
    leave_count: int
    skipped_count: int
    sheet_info: Dict[str, List[str]] = None


@dataclass
class WeeklyReportData:
    week_start_date: date
    days: List[date]
    team_leads: List[str]
    employees_by_tl: Dict[str, List[EmployeeRecord]]
    daily_status: Dict[str, Dict[str, str]]  # employee_name -> day -> status
    stats: Dict[str, int]
    sheet_info: Dict[str, List[str]] = None


class ExcelReportGenerator:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__, config.logs_folder, config.log_level)

    def generate_daily_report(self, data: DailyReportData) -> str:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Team Lead Status Report"

        # Write week/sheet info at top
        current_row = 1
        if data.sheet_info:
            for team_name, sheet_names in data.sheet_info.items():
                sheet_names_str = ", ".join(sheet_names)
                ws.cell(row=current_row, column=1, value=f"{team_name}:")
                ws.cell(row=current_row, column=2, value=sheet_names_str)
                current_row += 1

        # Add a blank row
        current_row += 1

        # Write headers
        headers = ["Name", "Status", "Status Report Reviewed by TL"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
        current_row +=1

        # Write data rows
        for tl_name in sorted(data.team_leads):
            team_records = data.employees_by_tl.get(tl_name, [])

            # Determine team status
            non_skipped = []
            for rec in team_records:
                if rec.is_leave:
                    continue
                non_skipped.append(rec)

            all_completed = all(rec.status.lower() == "completed" for rec in non_skipped)
            team_status = "Completed" if all_completed else "Pending"

            # Write TL row
            tl_cell = ws.cell(row=current_row, column=1, value=tl_name)
            tl_cell.alignment = Alignment(horizontal="left", vertical="center")
            tl_cell.font = Font(bold=True)

            tl_status_cell = ws.cell(row=current_row, column=2, value=team_status)
            tl_status_cell.alignment = Alignment(horizontal="center", vertical="center")
            if team_status == "Completed":
                tl_status_cell.fill = PatternFill(start_color="CCFFCC", end_color="CCFFCC", fill_type="solid")
            else:
                tl_status_cell.fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")

            tl_review_cell = ws.cell(row=current_row, column=3, value="")
            tl_review_cell.alignment = Alignment(horizontal="center", vertical="center")
            current_row += 1

            # Write team member rows (skip the team lead themselves)
            for rec in team_records:
                if rec.employee_name == tl_name:
                    continue
                # Indent team member name
                emp_name = f"  └─ {rec.employee_name}"
                if rec.is_leave:
                    emp_name += " (On Leave)"

                emp_cell = ws.cell(row=current_row, column=1, value=emp_name)
                emp_cell.alignment = Alignment(horizontal="left", vertical="center")

                emp_status = rec.status
                if rec.is_leave:
                    emp_status = "Completed"

                emp_status_cell = ws.cell(row=current_row, column=2, value=emp_status)
                emp_status_cell.alignment = Alignment(horizontal="center", vertical="center")
                if emp_status == "Completed":
                    emp_status_cell.fill = PatternFill(start_color="CCFFCC", end_color="CCFFCC", fill_type="solid")
                elif emp_status == "Pending":
                    emp_status_cell.fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")

                emp_review_cell = ws.cell(row=current_row, column=3, value="")
                emp_review_cell.alignment = Alignment(horizontal="center", vertical="center")
                current_row += 1

        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        filename = f"status_report_{data.report_date.strftime('%Y-%m-%d')}_{data.scheduler_type.lower()}_{datetime.now().strftime('%H%M%S')}.xlsx"
        filepath = os.path.join(self.config.reports_folder, filename)
        wb.save(filepath)
        self.logger.info(f"Daily report generated: {filepath}")
        return filepath

    def generate_weekly_report(self, data: WeeklyReportData) -> str:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Team Lead Status Report"

        # Write week/sheet info at top
        current_row = 1
        if data.sheet_info:
            for team_name, sheet_names in data.sheet_info.items():
                sheet_names_str = ", ".join(sheet_names)
                ws.cell(row=current_row, column=1, value=f"{team_name}:")
                ws.cell(row=current_row, column=2, value=sheet_names_str)
                current_row += 1

        # Add a blank row
        current_row += 1

        # Write headers
        headers = ["Name", "Status", "Status Report Reviewed by TL"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
        current_row +=1

        # Write data rows
        for tl_name in sorted(data.team_leads):
            team_records = data.employees_by_tl.get(tl_name, [])

            # Determine team status
            non_skipped = []
            for rec in team_records:
                if rec.is_leave:
                    continue
                non_skipped.append(rec)

            all_completed = all(rec.status.lower() == "completed" for rec in non_skipped)
            team_status = "Completed" if all_completed else "Pending"

            # Write TL row
            tl_cell = ws.cell(row=current_row, column=1, value=tl_name)
            tl_cell.alignment = Alignment(horizontal="left", vertical="center")
            tl_cell.font = Font(bold=True)

            tl_status_cell = ws.cell(row=current_row, column=2, value=team_status)
            tl_status_cell.alignment = Alignment(horizontal="center", vertical="center")
            if team_status == "Completed":
                tl_status_cell.fill = PatternFill(start_color="CCFFCC", end_color="CCFFCC", fill_type="solid")
            else:
                tl_status_cell.fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")

            tl_review_cell = ws.cell(row=current_row, column=3, value="")
            tl_review_cell.alignment = Alignment(horizontal="center", vertical="center")
            current_row += 1

            # Write team member rows (skip the team lead themselves)
            for rec in team_records:
                if rec.employee_name == tl_name:
                    continue
                # Indent team member name
                emp_name = f"  └─ {rec.employee_name}"
                if rec.is_leave:
                    emp_name += " (On Leave)"

                emp_cell = ws.cell(row=current_row, column=1, value=emp_name)
                emp_cell.alignment = Alignment(horizontal="left", vertical="center")

                emp_status = rec.status
                if rec.is_leave:
                    emp_status = "Completed"

                emp_status_cell = ws.cell(row=current_row, column=2, value=emp_status)
                emp_status_cell.alignment = Alignment(horizontal="center", vertical="center")
                if emp_status == "Completed":
                    emp_status_cell.fill = PatternFill(start_color="CCFFCC", end_color="CCFFCC", fill_type="solid")
                elif emp_status == "Pending":
                    emp_status_cell.fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")

                emp_review_cell = ws.cell(row=current_row, column=3, value="")
                emp_review_cell.alignment = Alignment(horizontal="center", vertical="center")
                current_row += 1

        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        filename = f"status_report_week_ending_{data.week_start_date.strftime('%d-%m-%Y')}_{datetime.now().strftime('%H%M%S')}.xlsx"
        filepath = os.path.join(self.config.reports_folder, filename)
        wb.save(filepath)
        self.logger.info(f"Weekly report generated: {filepath}")
        return filepath
