# Onboarding & Hiring Dashboard

A full-fledged, browser-based onboarding & hiring dashboard built in **Python** with
**Streamlit** (web app framework) and **Plotly** (interactive charts). Data is read
from an Excel file, so you can plug in your real HRMS/ATS export.

## Features

- **Top banner** with a welcome/homepage message for the Hiring & Onboarding Hub
- **🔔 Notifications icon** — role-based, dynamically generated:
  - *Recruiter* → "John Doe's interview is due today"
  - *Employee* → "Complete onboarding trainings" / "Submit mandatory forms (Gratuity, Insurance, Payroll)"
  - *Project Manager* → "Help set up VDI / Team Connect"
  - *HR Admin* → aggregated org-wide alerts
- **☎️ Contact Us icon** — sample IT helpdesk toll-free number and email
- **KPI cards** — Total Employees, Employees Onboarded, Pending BGV, Hired This Week
- **Interactive charts** (Plotly) — hover over any chart segment to see the actual
  employee names in that bucket (onboarding status, BGV status, weekly hiring trend)
- **Excel export** — one-click download of a leadership-ready report
  (Summary + Employee Detail + Weekly Trend sheets)
- **Excel import** — upload your own data file from the sidebar at any time

## Project Structure

```
onboarding_dashboard/
├── app.py                     # Main Streamlit dashboard app
├── generate_sample_data.py    # Generates sample Excel data
├── requirements.txt
├── README.md
└── data/
    └── Employee_Data.xlsx     # Sample data (auto-generated)
```

## Setup (in Trae IDE or any terminal)

1. **Open this folder** in Trae IDE (File → Open Folder).

2. **Create a virtual environment** (recommended) and install dependencies:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Generate the sample data file** (only needed once, or whenever you want
   to regenerate fresh sample data):
   ```bash
   python generate_sample_data.py
   ```
   This creates `data/Employee_Data.xlsx`.

4. **Run the app** — this launches it in your default browser:
   ```bash
   streamlit run app.py
   ```
   It will open automatically at `http://localhost:8501`.

5. **Using your own real data**: use the "Import Employee Data (Excel)"
   uploader in the left sidebar to upload your own HRMS/ATS export instead
   of the sample file — see the required columns below.

## Excel Data Schema (required columns)

Your Excel file (first sheet) must contain these columns (case-sensitive):

| Column                | Description                                         | Example              |
|-----------------------|------------------------------------------------------|-----------------------|
| EmployeeID            | Unique employee/candidate ID                         | EMP1001               |
| EmployeeName          | Full name                                             | John Doe              |
| Department            | Department/team                                      | Engineering            |
| RecruiterName         | Assigned recruiter                                    | Ritu Sharma            |
| ProjectManagerName    | Assigned project manager                              | Karan Bajaj            |
| HireDate              | Date of hire (YYYY-MM-DD)                             | 2026-06-20             |
| InterviewDate         | Interview date (YYYY-MM-DD)                           | 2026-07-07             |
| InterviewStatus       | `Completed` / `Pending`                               | Pending                |
| OnboardingStatus      | `Completed` / `Pending`                               | Pending                |
| BGVStatus             | `Cleared` / `Pending`                                  | Pending                |
| TrainingStatus        | `Completed` / `Pending`                               | Pending                |
| MandatoryFormsStatus  | `Completed` / `Pending` (Gratuity/Insurance/Payroll)   | Pending                |
| VDIStatus             | `Setup` / `Pending`                                    | Pending                |
| TeamConnectStatus     | `Setup` / `Pending`                                    | Setup                  |

> Tip: if your real HR export uses different column names, either rename
> the columns in Excel before uploading, or edit `REQUIRED_COLUMNS` and the
> logic in `app.py` to match your schema.

## Customizing

- **IT Helpdesk number/email**: edit `IT_HELPDESK_TOLL_FREE` and
  `IT_HELPDESK_EMAIL` near the top of `app.py`.
- **Notification rules**: edit the `build_notifications()` function in
  `app.py` — this is where role-based alert logic lives.
- **Colors/branding**: edit the `<style>` block at the top of `app.py`.
- **Roles**: add/remove roles in the sidebar `st.selectbox` and extend
  `build_notifications()` accordingly.

## Notes on "automated browser app"

This app runs as a local web server (Streamlit) that opens in your default
browser — no separate browser-automation framework (e.g. Selenium/Playwright)
is needed for normal use, since Streamlit *is* the web app itself. If you
specifically need to automate clicking/testing this dashboard end-to-end
(e.g., for QA), Playwright or Selenium can be layered on top separately —
let me know if you'd like that added.
