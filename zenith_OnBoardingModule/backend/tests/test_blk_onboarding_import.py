from datetime import date

from openpyxl import Workbook

from app.services.blk_onboarding_import import parse_blk_workbook


def test_parse_blk_workbook_uses_phase1_names_not_resource_role_labels_and_normalizes_days(tmp_path) -> None:
    workbook = Workbook()
    resources = workbook.active
    resources.title = "Resource List"
    resources.append(["Tracker"])
    resources.append(["Employee ID", "VLinker", "Client", "Project"])
    resources.append([None, ".Net Developer", "Data Engineering", "Bud File SWAT"])

    phase = workbook.create_sheet("Phase1 - Machine Setup")
    phase.cell(2, 9, "Actual Employee")
    phase.cell(2, 10, "Second Employee")
    phase.cell(2, 11, " actual employee ")
    phase.cell(6, 2, "Week0-A")
    phase.cell(6, 3, "Setup")
    phase.cell(6, 4, "Request access")
    phase.cell(6, 5, "Submit the access form")
    phase.cell(7, 2, "Day1a")
    phase.cell(7, 4, "Meet the team")
    phase.cell(8, 2, "Day6")
    phase.cell(8, 4, "Out-of-scope item")

    path = tmp_path / "tracker.xlsx"
    workbook.save(path)

    employees, onboarding, activities = parse_blk_workbook(path)

    assert [employee["full_name"] for employee in employees] == ["Actual Employee", "Second Employee"]
    assert all("employee_id" not in employee for employee in employees)
    assert all("client" not in employee and "project" not in employee for employee in employees)
    assert [record["source_employee_name"] for record in onboarding] == ["Actual Employee", "Second Employee"]
    assert [activity["day"] for activity in activities] == ["Week0", "Day1"]
    assert activities[0]["activity"] == "Setup: Request access"
    assert activities[0]["action"] == "Submit the access form"
