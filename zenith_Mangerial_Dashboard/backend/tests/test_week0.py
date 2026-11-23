from bson import ObjectId

from app.api.v1.routes.week0 import (
    Week0RowPayload,
    _build_employee_activity_records,
    _build_employee_activity_updates,
    _deduplicate_seed_rows,
    _merge_employee_tracker_values,
    _normalize_status,
    _row_filter,
)


def test_normalize_status_accepts_complete_alias() -> None:
    assert _normalize_status("Complete") == "Completed"
    assert _normalize_status("completed") == "Completed"
    assert _normalize_status("Pending") == "Pending"


def test_build_employee_activity_records_maps_employee_to_tracker_rows() -> None:
    employees = [{"employee_id": "EMP-100"}, {"employee_id": "EMP-200"}]
    rows = [
        {"_id": "a1", "day": "Day1", "activity": "Laptop setup", "status": "Completed", "blocker": "", "time_taken": "2h"},
        {"_id": "b2", "day": "Day2", "activity": "Security training", "status": "Pending", "blocker": "Firewall", "time_taken": ""},
    ]

    records = _build_employee_activity_records(employees, rows)

    assert records == [
        {
            "employee_id": "EMP-100",
            "activityid": "a1",
            "activity": "Laptop setup",
            "status": "Completed",
            "blocker": "",
            "time_taken": "2h",
            "day": "Day1",
        },
        {
            "employee_id": "EMP-100",
            "activityid": "b2",
            "activity": "Security training",
            "status": "Pending",
            "blocker": "Firewall",
            "time_taken": "",
            "day": "Day2",
        },
        {
            "employee_id": "EMP-200",
            "activityid": "a1",
            "activity": "Laptop setup",
            "status": "Completed",
            "blocker": "",
            "time_taken": "2h",
            "day": "Day1",
        },
        {
            "employee_id": "EMP-200",
            "activityid": "b2",
            "activity": "Security training",
            "status": "Pending",
            "blocker": "Firewall",
            "time_taken": "",
            "day": "Day2",
        },
    ]


def test_row_filter_matches_legacy_action_aliases() -> None:
    row_filter = _row_filter(
        {
            "day": "Day1",
            "activity": "Environment setup",
            "action": "Open the setup guide",
            "technology": "Applicable for all",
            "project": "Applicable for all projects",
        }
    )

    assert row_filter == {
        "source": "week0_tracker",
        "day": "Day1",
        "activity": "Environment setup",
        "technology": "Applicable for all",
        "$and": [
            {
                "$or": [
                    {"project": "Applicable for all projects"},
                    {"projects": "Applicable for all projects"},
                ]
            }
        ],
        "$or": [
            {"actions": "Open the setup guide"},
            {"action": "Open the setup guide"},
            {"relevantLink": "Open the setup guide"},
        ],
    }


def test_row_filter_matches_week0_alias_day() -> None:
    row_filter = _row_filter(
        {
            "day": "Week0",
            "activity": "Environment setup",
            "action": "Open the setup guide",
            "technology": "Applicable for all",
            "project": "Applicable for all projects",
        }
    )

    assert row_filter["day"] == {"$regex": "^week0(-a)?$", "$options": "i"}


def test_row_document_persists_completed_status() -> None:
    row = {
        "day": "Day1",
        "activity": "Laptop setup",
        "action": "Install tools",
        "technology": "Applicable for all",
        "project": "Applicable for all projects",
        "status": "Completed",
    }

    document = __import__("app.api.v1.routes.week0", fromlist=["_row_document"])._row_document(row)

    assert document["status"] == "Completed"


def test_build_phase_counts_uses_day0_as_week0() -> None:
    counts = __import__("app.api.v1.routes.week0", fromlist=["_build_phase_counts"])._build_phase_counts([
        {"day": "Day0", "status": "Completed"},
        {"day": "Day1", "status": "Pending"},
    ])

    assert counts["Week0"] == 1
    assert counts["Week0_completed"] == 1
    assert counts["Day1_pending"] == 1


def test_deduplicate_seed_rows_keeps_newest_duplicate() -> None:
    rows = [
        {
            "day": "Day1",
            "activity": "Environment setup",
            "action": "Open the setup guide",
            "technology": "Applicable for all",
            "project": "Applicable for all projects",
            "blocker": "Resolved blocker",
            "status": "Completed",
        },
        {
            "day": "Day1",
            "activity": "Environment setup",
            "action": "Open the setup guide",
            "technology": "Applicable for all",
            "project": "Applicable for all projects",
            "blocker": "Old blocker",
            "status": "Pending",
        },
    ]

    deduped_rows = _deduplicate_seed_rows(rows)

    assert len(deduped_rows) == 1
    assert deduped_rows[0]["id"] == 1
    assert deduped_rows[0]["blocker"] == "Resolved blocker"
    assert deduped_rows[0]["status"] == "Completed"


def test_week0_row_model_keeps_blocker_time_and_status() -> None:
    payload = Week0RowPayload.model_validate({
        "id": 1,
        "day": "Day1",
        "activity": "Laptop setup",
        "action": "Install tools",
        "relevantLink": "Install tools",
        "technology": "Applicable for all",
        "project": "Applicable for all projects",
        "blocker": "VPN access",
        "time_taken": "2h",
        "status": "Completed",
    })

    assert payload.blocker == "VPN access"
    assert payload.time_taken == "2h"
    assert payload.status == "Completed"


def test_row_document_excludes_employee_status_fields_from_tracker_rows() -> None:
    row_document = {
        "day": "Day1",
        "activity": "Laptop setup",
        "action": "Install tools",
        "technology": "Applicable for all",
        "project": "Applicable for all projects",
        "blocker": "VPN access",
        "time_taken": "2h",
        "status": "Completed",
    }

    result = {
        "source": "week0_tracker",
        "day": row_document["day"],
        "activity": row_document["activity"],
        "actions": row_document["action"],
        "action": row_document["action"],
        "relevantLink": row_document["action"],
        "technology": row_document["technology"],
        "projects": row_document["project"],
        "project": row_document["project"],
    }

    assert "blocker" not in result
    assert "time_taken" not in result
    assert "status" not in result


def test_employee_activity_records_do_not_include_removed_time_taken_field() -> None:
    employees = [{"employee_id": "EMP-200"}]
    rows = [
        {"_id": "a1", "day": "Day1", "activity": "Laptop setup", "status": "Completed", "blocker": "VPN access"},
        {"_id": "b2", "day": "Day1", "activity": "Security training", "status": "Pending", "blocker": ""},
    ]

    records = _build_employee_activity_records(employees, rows, employee_id="EMP-200")

    assert records[0]["employee_id"] == "EMP-200"
    assert "time_taken" not in records[0]
    assert "time_taken" not in records[1]


def test_build_employee_activity_records_filters_to_target_employee() -> None:
    employees = [{"employee_id": "EMP-100"}, {"employee_id": "EMP-200"}]
    object_id = ObjectId("64f000000000000000000001")
    rows = [
        {"_id": object_id, "day": "Day2", "activity": "Security training", "status": "Completed", "blocker": "", "time_taken": "1h"},
        {"_id": "b2", "day": "Day3", "activity": "Documentation", "status": "Pending", "blocker": "Need approval", "time_taken": ""},
    ]

    records = _build_employee_activity_records(employees, rows, employee_id="EMP-200")

    assert records == [
        {
            "employee_id": "EMP-200",
            "activityid": str(object_id),
            "activity": "Security training",
            "status": "Completed",
            "blocker": "",
            "time_taken": "1h",
            "day": "Day2",
        },
        {
            "employee_id": "EMP-200",
            "activityid": "b2",
            "activity": "Documentation",
            "status": "Pending",
            "blocker": "Need approval",
            "time_taken": "",
            "day": "Day3",
        },
    ]


def test_merge_employee_tracker_values_retains_status_blocker_and_time() -> None:
    template_rows = [
        {"id": 1, "day": "Day1", "activity": "Laptop setup", "action": "Install tools", "technology": "Applicable for all", "project": "Applicable for all projects"},
        {"id": 2, "day": "Day1", "activity": "Security training", "action": "Complete training", "technology": "Applicable for all", "project": "Applicable for all projects"},
    ]
    tracker_rows = [
        {"employee_id": "EMP-200", "activityid": "64f000000000000000000001", "activity": "Laptop setup", "status": "Completed", "blocker": "VPN access", "time_taken": "2h", "day": "Day1"},
        {"employee_id": "EMP-200", "activityid": "64f000000000000000000002", "activity": "Security training", "status": "Pending", "blocker": "", "time_taken": "", "day": "Day1"},
    ]

    merged_rows = _merge_employee_tracker_values(template_rows, tracker_rows, employee_id="EMP-200")

    assert merged_rows[0]["status"] == "Completed"
    assert merged_rows[0]["blocker"] == "VPN access"
    assert merged_rows[0]["time_taken"] == "2h"
    assert merged_rows[1]["status"] == "Pending"
    assert merged_rows[1]["blocker"] == ""
    assert merged_rows[1]["time_taken"] == ""


def test_merge_employee_tracker_values_marks_day_complete_when_all_day_rows_are_complete() -> None:
    template_rows = [
        {"id": 1, "day": "Day1", "activity": "Laptop setup", "action": "Install tools", "technology": "Applicable for all", "project": "Applicable for all projects"},
        {"id": 2, "day": "Day1", "activity": "Security training", "action": "Complete training", "technology": "Applicable for all", "project": "Applicable for all projects"},
        {"id": 3, "day": "Day2", "activity": "Policy review", "action": "Read policy", "technology": "Applicable for all", "project": "Applicable for all projects"},
    ]
    tracker_rows = [
        {"employee_id": "EMP-200", "activityid": "64f000000000000000000001", "activity": "Laptop setup", "status": "Completed", "blocker": "", "time_taken": "2h", "day": "Day1"},
        {"employee_id": "EMP-200", "activityid": "64f000000000000000000002", "activity": "Security training", "status": "Completed", "blocker": "", "time_taken": "1h", "day": "Day1"},
        {"employee_id": "EMP-200", "activityid": "64f000000000000000000003", "activity": "Policy review", "status": "Pending", "blocker": "Need approval", "time_taken": "", "day": "Day2"},
    ]

    merged_rows = _merge_employee_tracker_values(template_rows, tracker_rows, employee_id="EMP-200")

    assert merged_rows[0]["status"] == "Completed"
    assert merged_rows[1]["status"] == "Completed"
    assert merged_rows[2]["status"] == "Pending"


def test_merge_employee_tracker_values_uses_employee_day_activity_key() -> None:
    template_rows = [
        {"id": 1, "day": "Day1", "activity": "Laptop setup", "action": "Install tools", "technology": "Applicable for all", "project": "Applicable for all projects"},
        {"id": 2, "day": "Day2", "activity": "Laptop setup", "action": "Install tools", "technology": "Applicable for all", "project": "Applicable for all projects"},
    ]
    tracker_rows = [
        {"employee_id": "EMP-200", "activityid": "64f000000000000000000001", "activity": "Laptop setup", "status": "Completed", "blocker": "VPN access", "time_taken": "2h", "day": "Day1"},
        {"employee_id": "EMP-200", "activityid": "64f000000000000000000002", "activity": "Laptop setup", "status": "Pending", "blocker": "", "time_taken": "", "day": "Day2"},
    ]

    merged_rows = _merge_employee_tracker_values(template_rows, tracker_rows, employee_id="EMP-200")

    assert merged_rows[0]["status"] == "Completed"
    assert merged_rows[1]["status"] == "Pending"


def test_build_employee_activity_records_deduplicates_same_employee_activity() -> None:
    employees = [{"employee_id": "EMP-200"}]
    object_id = ObjectId("64f000000000000000000001")
    rows = [
        {"_id": object_id, "day": "Day1", "activity": "Laptop setup", "status": "Completed", "blocker": "VPN access", "time_taken": "2h"},
        {"_id": object_id, "day": "Day1", "activity": "Laptop setup", "status": "Completed", "blocker": "Resolved", "time_taken": "3h"},
    ]

    records = _build_employee_activity_records(employees, rows, employee_id="EMP-200")

    assert len(records) == 1
    assert records[0]["activityid"] == str(object_id)
    assert records[0]["blocker"] == "Resolved"
    assert records[0]["time_taken"] == "3h"


def test_build_employee_activity_updates_uses_current_completed_status_for_employee() -> None:
    object_id = ObjectId("64f000000000000000000001")
    payload_rows = [
        {
            "id": 1,
            "day": "Day1",
            "activity": "Laptop setup",
            "action": "Install tools",
            "technology": "Applicable for all",
            "project": "Applicable for all projects",
            "blocker": "VPN access",
            "time_taken": "2h",
            "status": "Completed",
        }
    ]
    stored_rows = [{"_id": object_id, "day": "Day1", "activity": "Laptop setup"}]

    updates = _build_employee_activity_updates(["EMP-200"], payload_rows, stored_rows)

    assert updates == [{
        "employee_id": "EMP-200",
        "activityid": str(object_id),
        "activity": "Laptop setup",
        "status": "Completed",
        "blocker": "VPN access",
        "time_taken": "2h",
        "day": "Day1",
    }]


def test_merge_employee_tracker_values_isolates_employee_specific_state() -> None:
    template_rows = [
        {"id": 1, "day": "Day1", "activity": "Laptop setup", "action": "Install tools", "technology": "Applicable for all", "project": "Applicable for all projects"},
        {"id": 2, "day": "Day1", "activity": "Security training", "action": "Complete training", "technology": "Applicable for all", "project": "Applicable for all projects"},
    ]
    tracker_rows = [
        {"employee_id": "EMP-200", "activityid": "64f000000000000000000001", "activity": "Laptop setup", "status": "Completed", "blocker": "VPN access", "time_taken": "2h", "day": "Day1"},
        {"employee_id": "EMP-300", "activityid": "64f000000000000000000002", "activity": "Security training", "status": "Completed", "blocker": "Data issue", "time_taken": "4h", "day": "Day1"},
    ]

    merged_rows = _merge_employee_tracker_values(template_rows, tracker_rows, employee_id="EMP-200")

    assert merged_rows[0]["status"] == "Completed"
    assert merged_rows[0]["blocker"] == "VPN access"
    assert merged_rows[0]["time_taken"] == "2h"
    assert merged_rows[1]["status"] == "Pending"
    assert merged_rows[1]["blocker"] == ""
    assert merged_rows[1]["time_taken"] == ""