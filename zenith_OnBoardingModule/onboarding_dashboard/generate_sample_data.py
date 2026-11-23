
"""
generate_sample_data.py
------------------------
Creates a sample Excel file (data/Employee_Data.xlsx) that mimics the kind of
HR export you would receive from an ATS / HRMS system. The dashboard app.py
reads from a file with this exact structure, so you can simply replace
data/Employee_Data.xlsx with your own real export as long as the column
names match.

Run once:
    python generate_sample_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

FIRST_NAMES = [
    "John", "Priya", "Amit", "Sara", "Michael", "Ananya", "David", "Neha",
    "Rahul", "Emily", "Vikram", "Sneha", "Chris", "Pooja", "Arjun", "Kavya",
    "Rohan", "Isha", "Karan", "Divya", "Suresh", "Meera", "Aditya", "Riya",
    "Nikhil", "Tanya", "Sameer", "Aarti", "Varun", "Shreya"
]
LAST_NAMES = [
    "Doe", "Sharma", "Patel", "Khan", "Smith", "Iyer", "Miller", "Gupta",
    "Verma", "Johnson", "Singh", "Reddy", "Brown", "Nair", "Mehta", "Kapoor",
    "Malhotra", "Chawla", "Bose", "Das", "Kumar", "Joshi", "Rao", "Bhat",
    "Agarwal", "Chopra", "Bansal", "Saxena", "Menon", "Pillai"
]

RECRUITERS = ["Ritu Sharma", "Alex Turner", "Sanjay Mehta", "Laura White"]
PROJECT_MANAGERS = ["Karan Bajaj", "Emma Wilson", "Deepak Rao", "Olivia James"]
DEPARTMENTS = ["Engineering", "Sales", "Marketing", "Finance", "HR", "Operations"]

# Define all onboarding actions with areas, days, etc.
ACTIONS = [
    # Onboarding trainings
    {"Action": "Onboarding Training - Company Policies", "Area": "Training", "DueDay": 1, "IsMandatory": True},
    {"Action": "Onboarding Training - IT Security", "Area": "Training", "DueDay": 2, "IsMandatory": True},
    {"Action": "Onboarding Training - Code of Conduct", "Area": "Training", "DueDay": 3, "IsMandatory": True},
    {"Action": "Onboarding Training - Team Introduction", "Area": "Team", "DueDay": 2, "IsMandatory": True},
    # Mandatory forms
    {"Action": "Submit Gratuity Form", "Area": "Forms", "DueDay": 5, "IsMandatory": True},
    {"Action": "Submit Insurance Form", "Area": "Forms", "DueDay": 5, "IsMandatory": True},
    {"Action": "Submit Payroll Details", "Area": "Forms", "DueDay": 3, "IsMandatory": True},
    # IT setup
    {"Action": "VDI Setup", "Area": "IT", "DueDay": 1, "IsMandatory": True},
    {"Action": "Laptop Issuance", "Area": "IT", "DueDay": 1, "IsMandatory": True},
    {"Action": "Email Account Setup", "Area": "IT", "DueDay": 1, "IsMandatory": True},
    {"Action": "Team Connect Setup", "Area": "IT", "DueDay": 2, "IsMandatory": True},
    # Background verification
    {"Action": "Background Verification Initiated", "Area": "HR", "DueDay": 0, "IsMandatory": True},
    {"Action": "Background Verification Completed", "Area": "HR", "DueDay": 10, "IsMandatory": True},
    # Day 2-5 activities
    {"Action": "Day 2 - Department Overview", "Area": "Onboarding", "DueDay": 2, "IsMandatory": True},
    {"Action": "Day 3 - Tools & Systems Training", "Area": "Training", "DueDay": 3, "IsMandatory": True},
    {"Action": "Day 4 - First Task Assignment", "Area": "Work", "DueDay": 4, "IsMandatory": True},
    {"Action": "Day 5 - Manager Check-in", "Area": "Manager", "DueDay": 5, "IsMandatory": True},
]

N_EMPLOYEES = 120
today = datetime.now()

rows = []
used_names = set()

for i in range(1, N_EMPLOYEES + 1):
    while True:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if name not in used_names:
            used_names.add(name)
            break

    # Hire date spread across the last 10 weeks (so we can build a weekly trend)
    days_ago = random.randint(0, 70)
    hire_date = today - timedelta(days=days_ago)

    # Interview date: mostly in the past, a handful today/upcoming (pending)
    interview_offset = random.choice([-10, -7, -5, -2, -1, 0, 0, 1])
    interview_date = today + timedelta(days=interview_offset)
    interview_status = "Completed" if interview_offset < 0 else "Pending"

    onboarding_status = random.choices(
        ["Completed", "Pending"], weights=[0.65, 0.35]
    )[0]
    bgv_status = random.choices(
        ["Cleared", "Pending"], weights=[0.7, 0.3]
    )[0]
    training_status = random.choices(
        ["Completed", "Pending"], weights=[0.6, 0.4]
    )[0]
    forms_status = random.choices(
        ["Completed", "Pending"], weights=[0.55, 0.45]
    )[0]
    vdi_status = random.choices(
        ["Setup", "Pending"], weights=[0.6, 0.4]
    )[0]
    team_connect_status = random.choices(
        ["Setup", "Pending"], weights=[0.6, 0.4]
    )[0]

    # Build row with base fields
    row = {
        "EmployeeID": f"EMP{1000 + i}",
        "EmployeeName": name,
        "Department": random.choice(DEPARTMENTS),
        "RecruiterName": random.choice(RECRUITERS),
        "ProjectManagerName": random.choice(PROJECT_MANAGERS),
        "HireDate": hire_date.strftime("%Y-%m-%d"),
        "InterviewDate": interview_date.strftime("%Y-%m-%d"),
        "InterviewStatus": interview_status,
        "OnboardingStatus": onboarding_status,
        "BGVStatus": bgv_status,
        "TrainingStatus": training_status,
        "MandatoryFormsStatus": forms_status,   # Gratuity / Insurance / Payroll
        "VDIStatus": vdi_status,
        "TeamConnectStatus": team_connect_status,
        "Day2ActivityStatus": random.choices(["Completed", "Pending"], weights=[0.6, 0.4])[0],
        "Day3ActivityStatus": random.choices(["Completed", "Pending"], weights=[0.55, 0.45])[0],
        "Day4ActivityStatus": random.choices(["Completed", "Pending"], weights=[0.5, 0.5])[0],
        "Day5ActivityStatus": random.choices(["Completed", "Pending"], weights=[0.45, 0.55])[0],
    }

    # Now add action statuses and dates
    for action in ACTIONS:
        action_key = action["Action"].replace(" ", "_").replace("-", "_")
        status = random.choices(["Completed", "Pending"], weights=[0.55, 0.45])[0]
        
        # Calculate due date based on hire date
        due_date = hire_date + timedelta(days=action["DueDay"])
        
        # Calculate completion date if status is completed
        completion_date = None
        if status == "Completed":
            # Complete some time between hire date and due date or a little after
            comp_offset = random.randint(-2, action["DueDay"])
            completion_date = hire_date + timedelta(days=comp_offset)
        
        row[f"{action_key}_Status"] = status
        row[f"{action_key}_DueDate"] = due_date.strftime("%Y-%m-%d")
        if completion_date:
            row[f"{action_key}_CompletionDate"] = completion_date.strftime("%Y-%m-%d")
        else:
            row[f"{action_key}_CompletionDate"] = ""

    rows.append(row)

df = pd.DataFrame(rows)

os.makedirs("data", exist_ok=True)
out_path = os.path.join("data", "Employee_Data.xlsx")
df.to_excel(out_path, index=False, sheet_name="Employees")

print(f"Sample data generated: {out_path}  ({len(df)} employee records)")

