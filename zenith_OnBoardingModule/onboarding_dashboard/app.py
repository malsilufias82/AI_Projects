"""
app.py - Modern BLK Onboarding Dashboard
"""

import io
import json
import logging
import os
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import dotenv_values
from openpyxl import load_workbook
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

from db import authenticate_user, get_user_by_id
from sla import (
    activity_day_number,
    activity_sla_deadlines,
    holiday_dates_from_records,
    parse_timestamp,
    sla_status,
)

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="TrackerSPhere - Onboarding Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
def load_css():
    try:
        with open("static/css/style.css", "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

# Session state initialization
# Load persisted session from file
SESSION_FILE = "current_session.json"

def load_session():
    if Path(SESSION_FILE).exists():
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                # If we have a persisted user, reload them from DB to get latest data (like role)
                if data.get("user") and data.get("user", {}).get("id"):
                    from db import get_user_by_id
                    db_user = get_user_by_id(data["user"]["id"])
                    if db_user:
                        data["user"] = dict(db_user)
                return data
        except Exception as e:
            print(f"Error loading session: {e}")
            return {"user": None, "authenticated": False}
    else:
        return {"user": None, "authenticated": False}

def save_session(user, authenticated):
    with open(SESSION_FILE, "w") as f:
        json.dump({"user": user, "authenticated": authenticated}, f)

# Initialize session state
persisted = load_session()
if "user" not in st.session_state:
    st.session_state.user = persisted["user"]
if "authenticated" not in st.session_state:
    st.session_state.authenticated = persisted["authenticated"]


def login_panel():
    st.markdown("<h1 style='text-align: center; color: #1f2937;'>Welcome to TrackerSPhere</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280;'>Please login or sign up to continue</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # Create tabs for login and sign up
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        
        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login", type="primary", use_container_width=True)
                
                if submit:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = dict(user)
                        st.session_state.authenticated = True
                        save_session(st.session_state.user, st.session_state.authenticated)
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password!")
        
        with signup_tab:
            with st.form("signup_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                role = st.selectbox("Select Role", ["Employee", "Project Manager (PM)"])
                
                # Get employee list for linking (if role is Employee)
                try:
                    df_resources, _, employee_names, _, _, _ = load_all_blk_data()
                except:
                    employee_names = []
                
                vlinker = None
                if role == "Employee" and employee_names:
                    vlinker = st.selectbox("Link to Employee (VLinker Name)", ["None"] + sorted(employee_names))
                
                submit_signup = st.form_submit_button("Sign Up", type="secondary", use_container_width=True)
                
                if submit_signup:
                    if not new_username or not new_password:
                        st.error("Username and password are required!")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match!")
                    else:
                        # Find employee_id if vlinker is selected
                        employee_id = None
                        if vlinker and vlinker != "None":
                            from db import get_employee_by_vlinker
                            emp = get_employee_by_vlinker(vlinker)
                            if emp:
                                employee_id = emp['id']
                        
                        # Register user
                        from db import register_user
                        user_id = register_user(new_username, new_password, 'PM' if role == 'Project Manager (PM)' else 'Employee', employee_id)
                        if user_id:
                            st.success("User created successfully! Please log in.")
                        else:
                            st.error("Username already exists!")


# Check if authenticated
if not st.session_state.authenticated:
    login_panel()
    st.stop()


DATA_PATH_DEFAULT = "data/BLK Onboarding Tracker.xlsx"
STATE_FILE_PATH = "onboarding_state.json"
SLA_STATE_FILE_PATH = "onboarding_sla_state.json"
IT_HELPDESK_TOLL_FREE = "1800 121 3350"
IT_HELPDESK_EMAIL = "HelpDesk@BlackRock.com"


def load_sla_state():
    if not Path(SLA_STATE_FILE_PATH).exists():
        return {"credentials_received_at": {}}

    with open(SLA_STATE_FILE_PATH, "r") as f:
        sla_state = json.load(f)
    if not isinstance(sla_state, dict):
        raise ValueError("Onboarding SLA state must be a JSON object.")
    credentials_received_at = sla_state.get("credentials_received_at", {})
    if not isinstance(credentials_received_at, dict):
        raise ValueError("Credential receipt timestamps must be a JSON object.")
    return {"credentials_received_at": credentials_received_at}


def save_sla_state(sla_state):
    with open(SLA_STATE_FILE_PATH, "w") as f:
        json.dump(sla_state, f, indent=2)


def get_mongodb_setting(name, default):
    value = os.environ.get(name)
    if value:
        return value
    backend_env_file = Path(__file__).resolve().parent.parent / "backend" / ".env"
    if backend_env_file.exists():
        return dotenv_values(backend_env_file).get(name) or default
    return default


@st.cache_data(ttl=300, show_spinner=False)
def load_yearly_holiday_dates(year):
    mongodb_url = get_mongodb_setting("MONGODB_URL", "mongodb://localhost:27017")
    database_name = get_mongodb_setting("MONGODB_DATABASE", "zenith")
    with MongoClient(mongodb_url, serverSelectionTimeoutMS=3000) as client:
        collection = client[database_name]["yearly_holiday"]
        records = list(
            collection.find(
                {"year": {"$in": [year, year + 1]}},
                {"_id": 0, "date": 1, "type": 1, "year": 1},
            )
        )
    if not any(record.get("year") == year for record in records):
        raise ValueError(
            f"No yearly_holiday records were found for {year}."
        )
    return holiday_dates_from_records(records)


def get_activity_sla(activity, task_data, credentials_received_at, holiday_dates, now):
    if activity_day_number(activity.get("day")) is None:
        return None, None

    task_data = task_data if isinstance(task_data, dict) else {"status": task_data}
    task_status = task_data.get("status", "Pending")
    if task_status == "Not Applicable":
        return "Not Applicable", None
    if credentials_received_at is None:
        return "SLA not calculated: enter credential receipt date and time", None
    if holiday_dates is None:
        return "SLA unavailable: holiday calendar could not be loaded", None

    deadline = activity_sla_deadlines(
        [activity], credentials_received_at, holiday_dates
    ).get(str(activity["id"]))
    if deadline is None:
        return None, None

    completed_at = None
    if task_status == "Done":
        completed_at = parse_timestamp(task_data.get("completed_at"))
        if completed_at is None:
            return "Completion time unavailable", deadline
    return sla_status(deadline, now, completed_at), deadline


def render_sla_status(status):
    status_colors = {
        "Within SLA": "#15803D",
        "SLA Warning": "#B45309",
        "SLA Breached": "#B91C1C",
        "Completion time unavailable": "#6B7280",
        "Not Applicable": "#6B7280",
    }
    color = status_colors.get(status, "#6B7280")
    return f'<span style="color:{color};font-weight:600;">{status}</span>'


# ----------------------------------------------------------------------------
# Data Loading & Parsing
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_all_blk_data():
    from openpyxl import load_workbook
    wb = load_workbook(DATA_PATH_DEFAULT, data_only=True)

    # Define which columns we want to keep (only green from both visual references plus BLK credentials)
    keep_columns = [
        "Employee ID", "Client", "Project", "VLinker", "Team Lead", 
        "Status", "Role Description", "Work Location", "Onboarding ", 
        "FTE/Contractor", "Current City", "Client Credential Received", "Skill set",
        "Pillar", "BLK Team/Sub Project", "Dev/QA"
    ]

    # Read Resource List
    ws_resources = wb["Resource List"]
    headers_resources = [cell.value for cell in ws_resources[2]]
    data_resources = []
    for row in ws_resources.iter_rows(min_row=3, values_only=True):
        if any(row):
            data_resources.append(row)
    df_resources = pd.DataFrame(data_resources, columns=headers_resources)
    df_resources = df_resources.dropna(axis=1, how="all")
    
    # Filter df_resources to only keep the desired columns
    # First, find which of our keep_columns actually exist in df_resources
    existing_keep_columns = [col for col in keep_columns if col in df_resources.columns]
    df_resources = df_resources[existing_keep_columns]

    # Read Phase1 - Machine Setup
    ws_phase1 = wb["Phase1 - Machine Setup"]
    employee_names = []
    employee_cols = {}
    employee_start_dates = {}
    employee_blk_cred_task_status = {}
    for col_idx in range(9, ws_phase1.max_column + 1):
        cell_val = ws_phase1.cell(row=2, column=col_idx).value
        if cell_val:
            name = str(cell_val).strip()
            if name and name not in employee_names:
                employee_names.append(name)
                employee_cols[name] = col_idx
                date_val = ws_phase1.cell(row=3, column=col_idx).value
                employee_start_dates[name] = date_val
                blk_cred_status = ws_phase1.cell(row=13, column=col_idx).value
                employee_blk_cred_task_status[name] = blk_cred_status

    activities = []
    employee_initial_status = {}
    
    for row_idx in range(6, ws_phase1.max_row + 1):
        day = ws_phase1.cell(row=row_idx, column=2).value
        area = ws_phase1.cell(row=row_idx, column=3).value
        action = ws_phase1.cell(row=row_idx, column=4).value
        how_to = ws_phase1.cell(row=row_idx, column=5).value
        if action:
            act_id = row_idx
            activities.append(
                {
                    "id": act_id,
                    "day": day,
                    "area": area,
                    "action": action,
                    "how_to": how_to,
                }
            )
            
            for emp_name, col_idx in employee_cols.items():
                status_val = ws_phase1.cell(row=row_idx, column=col_idx).value
                if emp_name not in employee_initial_status:
                    employee_initial_status[emp_name] = {}
                if status_val:
                    status_str = str(status_val).strip()
                    if "done" in status_str.lower():
                        employee_initial_status[emp_name][str(act_id)] = "Done"
                    elif "in progress" in status_str.lower():
                        employee_initial_status[emp_name][str(act_id)] = "In Progress"
                    elif "awaited" in status_str.lower():
                        employee_initial_status[emp_name][str(act_id)] = "Awaited"
                    elif "not applicable" in status_str.lower() or "na" in status_str.lower():
                        employee_initial_status[emp_name][str(act_id)] = "Not Applicable"
                    else:
                        employee_initial_status[emp_name][str(act_id)] = status_str
                else:
                    employee_initial_status[emp_name][str(act_id)] = "Pending"

    def clean_dates(df):
        for col in df.columns:
            col_str = str(col).lower()
            if "date" in col_str or "day" in col_str:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    df_resources = clean_dates(df_resources)

    return df_resources, activities, employee_names, employee_initial_status, employee_start_dates, employee_blk_cred_task_status

# ----------------------------------------------------------------------------
# State Management
# ----------------------------------------------------------------------------
def load_state(employee_initial_status):
    existing_state = {}
    if Path(STATE_FILE_PATH).exists():
        try:
            with open(STATE_FILE_PATH, "r") as f:
                existing_state = json.load(f)
        except:
            existing_state = {}
    
    merged_state = {}
    for emp_name, initial_status in employee_initial_status.items():
        merged_state[emp_name] = {}
        for task_id, status_val in initial_status.items():
            # Check if existing state has task_id
            existing_emp_state = existing_state.get(emp_name, {})
            if task_id in existing_emp_state:
                if isinstance(existing_emp_state[task_id], dict):
                    # Already new format: {"status": "...", "comment": "..."}
                    merged_state[emp_name][task_id] = existing_emp_state[task_id]
                else:
                    # Migrate old format (string status to dict)
                    merged_state[emp_name][task_id] = {
                        "status": existing_emp_state[task_id],
                        "comment": ""
                    }
            else:
                # Use initial status
                merged_state[emp_name][task_id] = {
                    "status": status_val,
                    "comment": ""
                }
    
    # Add any existing employees not in initial_status
    for emp_name in existing_state:
        if emp_name not in merged_state:
            merged_state[emp_name] = {}
            for task_id, task_data in existing_state[emp_name].items():
                if isinstance(task_data, dict):
                    merged_state[emp_name][task_id] = task_data
                else:
                    merged_state[emp_name][task_id] = {
                        "status": task_data,
                        "comment": ""
                    }
            
    return merged_state

def save_state(state):
    with open(STATE_FILE_PATH, "w") as f:
        json.dump(state, f, indent=2)

# ----------------------------------------------------------------------------
# Helper Components
# ----------------------------------------------------------------------------
def render_kpi_card(icon, label, value, trend=None, trend_up=True):
    trend_html = ""
    if trend:
        trend_class = "up" if trend_up else "down"
        trend_icon = "↑" if trend_up else "↓"
        trend_html = f'<div class="kpi-trend {trend_class}">{trend_icon} {trend}</div>'
    
    return f"""
    <div class="kpi-card fade-in">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {trend_html}
    </div>
    """

def render_status_badge(status):
    status_classes = {
        "Done": "status-done",
        "In Progress": "status-in-progress",
        "Pending": "status-pending",
        "Not Applicable": "status-not-applicable",
        "Awaited": "status-awaited"
    }
    cls = status_classes.get(status, "status-not-applicable")
    return f'<span class="status-badge {cls}">{status}</span>'

def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
def render_sidebar(df_resources, employee_names):
    with st.sidebar:
        # App Logo & Name
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="width: 80px; height: 80px; border-radius: 20px; background: linear-gradient(135deg, #2563EB 0%, #1E3A8A 50%, #10B981 100%); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);">
                <span style="font-size: 40px;">🌐</span>
            </div>
            <h2 style="margin: 0; font-size: 24px; font-weight: 800; color: #1F2937; letter-spacing: -0.5px;">TrackerSPhere</h2>
            <p style="margin: 6px 0 0; font-size: 13px; color: #6B7280; font-weight: 500;">Onboarding Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Role from logged-in user
        user = st.session_state.user
        role = "Project Manager" if user['role'] == 'PM' else "Employee"
        st.markdown(f"👤 **Role**: {role}")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📊 Navigation")
        
        nav_items = [
            ("Dashboard", "🏠"),
            ("Employees", "👥"),
            ("Tasks", "📋"),
            ("Reports", "📈"),
            ("Settings", "⚙️")
        ]
        
        selected_nav = st.selectbox("Select page", [item[0] for item in nav_items], index=0)
        
        st.markdown("---")
        
        # Filters
        st.markdown("### 🔍 Filters")
        
        filter_by = "None"
        selected_value = "All"
        selected_team_member = "All"
        selected_employee = None
        filtered_employee_names = employee_names.copy()
        selected_tech = "All"  # Technology/Skill
        selected_role_desc = "All"
        
        # Technology/Skill filter (using "VLinker" column from df_resources)
        if "VLinker" in df_resources.columns:
            unique_tech = sorted(df_resources["VLinker"].dropna().astype(str).unique().tolist())
            selected_tech = st.selectbox(
                "Select Technology/Skill", 
                ["All"] + unique_tech
            )
        
        # Role Description (Label) filter
        if "Role Description" in df_resources.columns:
            # First, filter df to get role descriptions based on selected tech
            df_role_filter = df_resources.copy()
            if selected_tech != "All" and "VLinker" in df_role_filter.columns:
                df_role_filter = df_role_filter[df_role_filter["VLinker"].astype(str) == selected_tech]
            unique_role_desc = sorted(df_role_filter["Role Description"].dropna().astype(str).unique().tolist())
            selected_role_desc = st.selectbox(
                "Select Role Description (Label)", 
                ["All"] + unique_role_desc
            )
        
        if role == "Employee":
            # For Employee: "Select Your Name" shows employee_names, possibly filtered
            all_employee_options = filtered_employee_names.copy()
            
            # If user has employee_id linked, use that employee
            from db import get_employee_by_id
            selected_employee = None
            if user.get('employee_id'):
                emp = get_employee_by_id(user['employee_id'])
                if emp:
                    selected_employee = emp['vlinker']
            if not selected_employee and all_employee_options:
                selected_employee = st.selectbox("Select Your Name", sorted(all_employee_options))
            elif all_employee_options:
                st.selectbox("Select Your Name", sorted(all_employee_options), 
                             index=(all_employee_options.index(selected_employee) if selected_employee in all_employee_options else 0))
        else:
            filter_by = st.selectbox(
                "Filter by", ["None", "Pillar", "BLK Team", "Team Lead"]
            )
            if filter_by != "None" and filter_by in df_resources.columns:
                # First filter df by tech and role description to get unique values for this filter
                df_filter_vals = df_resources.copy()
                if selected_tech != "All" and "VLinker" in df_filter_vals.columns:
                    df_filter_vals = df_filter_vals[df_filter_vals["VLinker"].astype(str) == selected_tech]
                if selected_role_desc != "All" and "Role Description" in df_filter_vals.columns:
                    df_filter_vals = df_filter_vals[df_filter_vals["Role Description"].astype(str) == selected_role_desc]
                unique_vals = sorted(df_filter_vals[filter_by].dropna().astype(str).unique().tolist())
                selected_value = st.selectbox(
                    f"Select {filter_by}", ["All"] + unique_vals
                )

            # Apply all filters for PM view
            # For PM, filtered_employee_names is employee_names (from Phase1)
            filtered_employee_names = employee_names.copy()
            
            selected_team_member = st.selectbox(
                "Select Team Member",
                ["All"] + sorted(filtered_employee_names)
            )
            
            if selected_team_member != "All":
                filtered_employee_names = [selected_team_member]
        
        st.markdown("---")
        
        return role, selected_employee, filtered_employee_names

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
def render_header(notifications):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        greeting = get_greeting()
        user = st.session_state.user
        st.markdown(f"""
        <div style="margin-bottom: 24px;">
            <h2 style="margin:0; font-size:28px; font-weight:700; color:#1F2937;">{greeting}! Welcome to <span style="color: #2563EB;">TrackerSPhere</span> 👋</h2>
            <p style="margin:8px 0 0; font-size:15px; color:#6B7280;">Track onboarding progress across your organization.</p>
            <p style="margin:4px 0 0; font-size:13px; color:#9CA3AF;">{datetime.now().strftime("%A, %B %d, %Y")}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Actions (aligned to the right with small, evenly spaced columns)
        # Use very small column ratios to keep icons close together
        action_col1, action_col2, action_col3, action_col4 = st.columns([0.3, 0.3, 0.3, 1])
        
        with action_col1:
            with st.popover(f"🔔 {len(notifications)}", use_container_width=True):
                st.markdown(f"**Notifications**")
                if not notifications:
                    st.write("You're all caught up! 🎉")
                else:
                    for text, urgent in notifications:
                        st.markdown(f"<div style='padding:12px; border-radius:8px; background:#f8fafc; margin-bottom:8px;'>{text}</div>", unsafe_allow_html=True)
        
        with action_col2:
            with st.popover("☎️", use_container_width=True):
                st.markdown("**BLK IT Helpdesk**")
                st.markdown(f"📞 Toll-Free: **{IT_HELPDESK_TOLL_FREE}**")
                st.markdown(f"✉️ Email: **{IT_HELPDESK_EMAIL}**")
                st.markdown("🕘 Available: Mon–Fri, 9 AM – 7 PM")
                st.caption("For urgent access/system issues, call the toll-free number!")
        
        with action_col3:
            with st.popover("⚙️", use_container_width=True):
                st.markdown("### ⚙️ Settings")
                st.markdown("---")
                st.markdown("#### 🎨 Theme")
                theme = st.selectbox("Select theme", ["Light", "Dark"], index=0, key="theme_selector")
                st.markdown("---")
                st.markdown("#### 👤 Profile")
                st.markdown(f"Signed in as **{user['username']}**")
                st.markdown(f"Role: **{'Project Manager' if user['role'] == 'PM' else 'Employee'}**")
        
        with action_col4:
            if st.button("Logout", type="secondary", use_container_width=True):
                st.session_state.user = None
                st.session_state.authenticated = False
                save_session(st.session_state.user, st.session_state.authenticated)
                st.rerun()

# ----------------------------------------------------------------------------
# Quick Actions
# ----------------------------------------------------------------------------
def render_quick_actions():
    st.markdown("#### ⚡ Quick Actions")
    cols = st.columns(5)
    actions = [
        ("➕ Add Employee", "primary"),
        ("✅ Add Task", "secondary"),
        ("📤 Export Report", "secondary"),
        ("📥 Import Data", "secondary"),
        ("📧 Send Reminder", "secondary")
    ]
    for i, (col, (label, style)) in enumerate(zip(cols, actions)):
        with col:
            if i == 0:  # Add Employee button
                if st.button(label, type="primary", use_container_width=True):
                    st.session_state.show_add_employee = not st.session_state.get("show_add_employee", False)
            elif i == 1:  # Add Task button
                if st.button(label, type="secondary", use_container_width=True):
                    st.session_state.show_add_task = not st.session_state.get("show_add_task", False)
            elif i == 2:  # Export Report button
                if st.button(label, type="secondary", use_container_width=True):
                    st.session_state.show_export = not st.session_state.get("show_export", False)
            elif i == 3:  # Import Data button
                if st.button(label, type="secondary", use_container_width=True):
                    st.session_state.show_import = not st.session_state.get("show_import", False)
            else:
                st.button(label, use_container_width=True)
    st.write("")

# ----------------------------------------------------------------------------
# Main Dashboard
# ----------------------------------------------------------------------------
def render_pm_dashboard(
    filtered_employee_names,
    activities,
    state,
    df_resources,
    employee_start_dates,
    employee_blk_cred_task_status,
    sla_state,
    holiday_dates_by_employee,
):
    # Calculate KPI metrics
    total_vlinkers = len(filtered_employee_names)
    total_tasks = total_vlinkers * len(activities)
    completed_tasks = 0
    in_progress_tasks = 0
    pending_tasks = 0
    
    # Calculate BLK Onboarded Vlinkers (those who have BLK credentials)
    blk_onboarded = 0
    for emp in filtered_employee_names:
        # Check if they have received BLK credentials
        cred_date = None
        if len(df_resources) > 0:
            # Find the right column for employee name
            emp_col = None
            for col in df_resources.columns:
                if "vlinker" in str(col).lower() or "employee" in str(col).lower() or "name" in str(col).lower():
                    emp_col = col
                    break
            
            if emp_col:
                emp_matches = df_resources[df_resources[emp_col].astype(str).str.strip() == emp.strip()]
                if len(emp_matches) > 0:
                    # Check BLK Credentials Received column
                    for col in df_resources.columns:
                        if "credential" in str(col).lower() or "blk" in str(col).lower():
                            cred_val = emp_matches.iloc[0][col]
                            if pd.notna(cred_val) and str(cred_val).strip() != "":
                                cred_date = cred_val
                                break
        
        # Also check BLK Credentials task status from Phase1 sheet
        blk_task_status = employee_blk_cred_task_status.get(emp, "")
        
        is_onboarded = False
        if cred_date is not None:
            is_onboarded = True
        elif blk_task_status and "done" in str(blk_task_status).lower():
            is_onboarded = True
        
        if is_onboarded:
            blk_onboarded += 1
    
    for emp in filtered_employee_names:
        emp_state = state.get(emp, {})
        for act in activities:
            act_id = str(act["id"])
            task_data = emp_state.get(act_id, {})
            status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
            if status == "Done":
                completed_tasks += 1
            elif status == "In Progress":
                in_progress_tasks += 1
            elif status in ["Pending", "Awaited"]:
                pending_tasks += 1
    
    # KPI Cards
    st.markdown("#### 📈 Overview")
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("🏢", "BLK Onboarded", blk_onboarded, f"{blk_onboarded}/{total_vlinkers}", True),
        ("📋", "Pending Tasks", pending_tasks, "-5 from yesterday", False),
        ("✅", "Completed", completed_tasks, "+12 today", True),
        ("⏳", "In Progress", in_progress_tasks, "+3 today", True)
    ]
    for col, (icon, label, value, trend, trend_up) in zip([k1, k2, k3, k4], kpis):
        with col:
            st.markdown(render_kpi_card(icon, label, value, trend, trend_up), unsafe_allow_html=True)
    
    st.write("")
    
    # Quick Actions
    render_quick_actions()
    
    st.write("")
    
    # Show Export Form if button was clicked
    if st.session_state.get("show_export", False):
        st.markdown("#### 📤 Export Reports")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            render_export(state, filtered_employee_names, activities, df_resources)
        with col_e2:
            st.markdown("##### Export Options")
            st.write("- Exports Onboarding Progress Summary and Resource List")
            st.write("- File name includes today's date")
    
    st.write("")
    
    # Show Import Form if button was clicked
    if st.session_state.get("show_import", False):
        st.markdown("#### 📥 Import New Vlinkers")
        
        uploaded_file = st.file_uploader(
            "Upload Excel file with new Vlinkers",
            type=["xlsx", "xls"],
            help="Upload an Excel file with columns matching the Resource List format"
        )
        
        if uploaded_file is not None:
            try:
                # Read uploaded Excel file
                uploaded_df = pd.read_excel(uploaded_file, engine="openpyxl")
                st.markdown("##### Preview of Uploaded Data")
                st.dataframe(uploaded_df.head())
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Import Data to Resource List", type="primary", use_container_width=True):
                        # Load workbook
                        wb = load_workbook(DATA_PATH_DEFAULT)
                        ws_resource = wb["Resource List"]
                        
                        # Find the first empty row in Resource List
                        next_row = 3
                        while ws_resource.cell(row=next_row, column=4).value is not None:
                            next_row += 1
                        
                        # Get column headers to map columns
                        headers = [cell.value for cell in ws_resource[2]]
                        header_to_col = {str(h).strip() if h is not None else f"col_{i}": i+1 for i, h in enumerate(headers)}
                        
                        # Import each row from uploaded data
                        imported_count = 0
                        for _, row in uploaded_df.iterrows():
                            for col_name, col_idx in header_to_col.items():
                                if col_name in row:
                                    ws_resource.cell(row=next_row, column=col_idx, value=row[col_name])
                            next_row +=1
                            imported_count +=1
                        
                        # Save the workbook
                        wb.save(DATA_PATH_DEFAULT)
                        
                        # Update Phase1 sheet to add columns for new Vlinkers (optional)
                        st.success(f"✅ Successfully imported {imported_count} new Vlinkers!")
                        st.cache_data.clear()
                        st.session_state.show_import = False
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.show_import = False
                        st.rerun()
            
            except Exception as e:
                st.error(f"Error importing file: {str(e)}")
    
    st.write("")
    
    # Show Add Employee Form if button was clicked
    if st.session_state.get("show_add_employee", False):
        st.markdown("#### ➕ Add New Vlink Employee")
        
        # Define ALL GREEN fields from both visual references (name and Excel column, 1-based)
        green_header_defs = [
            {"name": "Employee ID", "excel_col":1},
            {"name": "Client", "excel_col":2},
            {"name": "Project", "excel_col":3},
            {"name": "VLinker", "excel_col":6},
            {"name": "Team Lead", "excel_col":7},
            {"name": "Status", "excel_col":12},
            {"name": "Role Description", "excel_col":13},
            {"name": "Work Location", "excel_col":15},
            {"name": "Onboarding", "excel_col":26},
            {"name": "FTE/Contractor", "excel_col":52},
            {"name": "Current City", "excel_col":60},
        ]
        
        # All fields are just the green fields
        all_fields = green_header_defs
        
        with st.form("add_employee_form"):
            num_cols = 2
            cols = st.columns(num_cols)
            field_inputs = {}
            
            # Create inputs for all fields
            for i, field in enumerate(all_fields):
                col = cols[i % num_cols]
                with col:
                    # Make VLinker and Team Lead required
                    is_required = field["name"] in ["VLinker", "Team Lead"]
                    label = f"{field['name']}{' (required)' if is_required else ''}"
                    if field["name"] == "Status":
                        field_inputs[field["excel_col"]] = st.selectbox(label, ["Active", "Inactive"], key=f"add_emp_{field['excel_col']}")
                    else:
                        field_inputs[field["excel_col"]] = st.text_input(label, key=f"add_emp_{field['excel_col']}")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("Add Employee", use_container_width=True, type="primary")
            with col_cancel:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_add_employee = False
                    st.rerun()
            
            if submitted:
                # Check required fields
                vlinker_val = field_inputs.get(6, "")  # VLinker is excel_col 6
                team_lead_val = field_inputs.get(7, "")  # Team Lead is excel_col7
                if not vlinker_val or not team_lead_val:
                    st.error("VLinker and Team Lead are required!")
                else:
                    try:
                        from openpyxl import load_workbook
                        wb = load_workbook(DATA_PATH_DEFAULT)
                        
                        # Write to Resource List sheet
                        ws_resource = wb["Resource List"]
                        next_resource_row = 3
                        while ws_resource.cell(row=next_resource_row, column=6).value is not None:  # check VLinker column (col6)
                            next_resource_row += 1
                        
                        # Write all fields
                        for excel_col, val in field_inputs.items():
                            if val:
                                ws_resource.cell(row=next_resource_row, column=excel_col, value=val)
                        
                        # Also add to Phase1 - Machine Setup sheet as before
                        ws_phase1 = wb["Phase1 - Machine Setup"]
                        next_phase1_col = 9
                        while ws_phase1.cell(row=2, column=next_phase1_col).value is not None:
                            next_phase1_col += 1
                        ws_phase1.cell(row=2, column=next_phase1_col, value=vlinker_val)
                        ws_phase1.cell(row=3, column=next_phase1_col, value="Week0")
                        ws_phase1.cell(row=4, column=next_phase1_col, value="Shubhanshu")
                        
                        wb.save(DATA_PATH_DEFAULT)
                        st.success(f"Successfully added new employee: {vlinker_val}")
                        st.cache_data.clear()
                        st.session_state.show_add_employee = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding employee: {str(e)}")
        st.write("")
    
    # Show Add Task Form if button was clicked
    if st.session_state.get("show_add_task", False):
        st.markdown("#### ✅ Add New Task")
        
        with st.form("add_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_day = st.text_input("Day/Week (e.g., Week0, Week1)", placeholder="Week0")
                new_area = st.text_input("Area (e.g., Training Sessions)", placeholder="Training Sessions")
                new_action = st.text_input("Task/Action", placeholder="e.g., Onboarding Training(14 January 2026)")
            
            with col2:
                new_how_to = st.text_area("How To Complete", placeholder="Instructions on how to complete the task")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("Add Task", use_container_width=True, type="primary")
            with col_cancel:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_add_task = False
                    st.rerun()
            
            if submitted:
                if not new_day or not new_area or not new_action:
                    st.error("Day, Area, and Task/Action are required!")
                else:
                    try:
                        from openpyxl import load_workbook
                        wb = load_workbook(DATA_PATH_DEFAULT)
                        ws = wb["Phase1 - Machine Setup"]
                        
                        # Find the last task row - look for where column 4 (Actions) has data
                        last_task_row = 6
                        while ws.cell(row=last_task_row + 1, column=4).value is not None:
                            last_task_row += 1
                        
                        new_task_row = last_task_row + 1
                        
                        # Write the new task
                        ws.cell(row=new_task_row, column=2, value=new_day)  # Column B: Day
                        ws.cell(row=new_task_row, column=3, value=new_area)  # Column C: Area
                        ws.cell(row=new_task_row, column=4, value=new_action)  # Column D: Actions
                        ws.cell(row=new_task_row, column=5, value=new_how_to)  # Column E: How To
                        
                        # Initialize status for all employees as "Pending"
                        # Find first employee column - starts at 9
                        emp_col = 9
                        while ws.cell(row=2, column=emp_col).value is not None:
                            ws.cell(row=new_task_row, column=emp_col, value="Pending")
                            emp_col += 1
                        
                        # Save and reset
                        wb.save(DATA_PATH_DEFAULT)
                        st.success(f"Successfully added new task: {new_action}")
                        st.cache_data.clear()
                        st.session_state.show_add_task = False
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error adding task: {str(e)}")
        st.write("")
    
    st.write("")
    
    # Detailed view
    st.markdown("#### 👥 Detailed Employee Onboarding Status")
    selected_emp_detail = st.selectbox(
        "Select an employee to view their tasks",
        ["-- Select --"] + filtered_employee_names
    )

    if selected_emp_detail and selected_emp_detail != "-- Select --":
        st.markdown(f"##### 📋 Tasks for {selected_emp_detail}")
        emp_state = state.get(selected_emp_detail, {})
        
        pending_awaited_acts = []
        for act in activities:
            act_id = str(act["id"])
            task_data = emp_state.get(act_id, {})
            status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
            if status in ["Pending", "Awaited"]:
                pending_awaited_acts.append(act)
        
        if not pending_awaited_acts:
            st.info(f"🎉 All tasks for {selected_emp_detail} are completed!")
        else:
            grouped_activities = {}
            for act in pending_awaited_acts:
                day = act["day"] or "Uncategorized"
                if day not in grouped_activities:
                    grouped_activities[day] = []
                grouped_activities[day].append(act)
            
            for day, acts in grouped_activities.items():
                with st.expander(f"📅 {day} ({len(acts)} pending tasks)", expanded=False):
                    for act in acts:
                        act_id = str(act["id"])
                        task_data = emp_state.get(act_id, {})
                        current_status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
                        current_comment = task_data.get("comment", "") if isinstance(task_data, dict) else ""
                        
                        # Check if this is an access-related task
                        is_access_task = "verify access" in act["action"].lower() or \
                                        "request access" in act["action"].lower() or \
                                        "verify access" in act["area"].lower() or \
                                        "request and/or verify access" in act["area"].lower()
                        
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**{act['area']}**: {act['action']}")
                            if act["how_to"]:
                                with st.expander("ℹ️ How to complete?"):
                                    st.write(act["how_to"])
                            if is_access_task:
                                with st.expander("💬 Remarks/Comments"):
                                    new_comment = st.text_area(
                                        "Add comments about time to complete or other details",
                                        value=current_comment,
                                        key=f"pm_comment_{selected_emp_detail}_{act_id}",
                                        height=80
                                    )
                                    if new_comment != current_comment:
                                        if selected_emp_detail not in state:
                                            state[selected_emp_detail] = {}
                                        if act_id not in state[selected_emp_detail] or not isinstance(state[selected_emp_detail][act_id], dict):
                                            state[selected_emp_detail][act_id] = {"status": current_status, "comment": ""}
                                        state[selected_emp_detail][act_id]["comment"] = new_comment
                                        save_state(state)
                                        st.success("Comment updated!")
                        with c2:
                            st.markdown(render_status_badge(current_status), unsafe_allow_html=True)
                            status_options = ["Pending", "In Progress", "Done", "Not Applicable", "Awaited"]
                            new_status = st.selectbox(
                                "",
                                status_options,
                                index=status_options.index(current_status) if current_status in status_options else 0,
                                key=f"pm_{selected_emp_detail}_{act_id}",
                                label_visibility="collapsed"
                            )
                            if new_status != current_status:
                                if selected_emp_detail not in state:
                                    state[selected_emp_detail] = {}
                                if act_id not in state[selected_emp_detail] or not isinstance(state[selected_emp_detail][act_id], dict):
                                    state[selected_emp_detail][act_id] = {"status": new_status, "comment": current_comment}
                                else:
                                    state[selected_emp_detail][act_id]["status"] = new_status
                                save_state(state)
                                st.success("Status updated!")
    
    st.write("")
    
    st.markdown("#### 📊 Onboarding Progress Summary")
    
    # Build progress summary data
    progress_summary = []
    task_lists = {}  # Store task lists by employee and status
    for emp in filtered_employee_names:
        emp_state = state.get(emp, {})
        total = len(activities)
        completed = 0
        in_progress = 0
        pending = 0
        awaited = 0
        not_applicable = 0
        
        task_lists[emp] = {
            "Total Tasks": activities,
            "Completed": [],
            "In Progress": [],
            "Pending": [],
            "Awaited": [],
            "Not Applicable": []
        }
        
        for act in activities:
            act_id = str(act["id"])
            task_data = emp_state.get(act_id, {})
            status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
            
            if status == "Done":
                completed +=1
                task_lists[emp]["Completed"].append(act)
            elif status == "In Progress":
                in_progress +=1
                task_lists[emp]["In Progress"].append(act)
            elif status == "Pending":
                pending +=1
                task_lists[emp]["Pending"].append(act)
            elif status == "Awaited":
                awaited +=1
                task_lists[emp]["Awaited"].append(act)
            elif status == "Not Applicable":
                not_applicable +=1
                task_lists[emp]["Not Applicable"].append(act)
        
        progress_percent = (completed / total) * 100 if total > 0 else 0
        progress_summary.append({
            "Employee": emp,
            "Total Tasks": total,
            "Completed": completed,
            "In Progress": in_progress,
            "Pending": pending,
            "Awaited": awaited,
            "Not Applicable": not_applicable,
            "Progress (%)": round(progress_percent, 1)
        })
    
    # Create custom table with proper alignment using only st.columns
    col_widths = [2, 1, 1, 1, 1, 1, 1, 1]
    
    # Header row
    header_cols = st.columns(col_widths)
    headers = ["Employee", "Total Tasks", "Completed", "In Progress", "Pending", "Awaited", "Not Applicable", "Progress (%)"]
    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")
    
    st.divider()
    
    # Data rows
    for idx, emp_row in enumerate(progress_summary):
        emp = emp_row["Employee"]
        
        # Create row columns
        row_cols = st.columns(col_widths)
        
        # Employee name
        row_cols[0].markdown(f"**{emp}**")
        
        # Total Tasks
        with row_cols[1].popover(str(emp_row["Total Tasks"]), use_container_width=True):
            st.markdown(f"**All Tasks for {emp}**")
            for task in task_lists[emp]["Total Tasks"]:
                st.markdown(f"• {task['day']} • {task['area']}: {task['action']}")
        
        # Completed
        with row_cols[2].popover(str(emp_row["Completed"]), use_container_width=True):
            st.markdown(f"**Completed Tasks for {emp}**")
            if task_lists[emp]["Completed"]:
                for task in task_lists[emp]["Completed"]:
                    st.markdown(f"• {task['day']} • {task['area']}: {task['action']}")
            else:
                st.write("No completed tasks")
        
        # In Progress
        with row_cols[3].popover(str(emp_row["In Progress"]), use_container_width=True):
            st.markdown(f"**In Progress Tasks for {emp}**")
            if task_lists[emp]["In Progress"]:
                for task in task_lists[emp]["In Progress"]:
                    st.markdown(f"• {task['day']} • {task['area']}: {task['action']}")
            else:
                st.write("No in-progress tasks")
        
        # Pending
        with row_cols[4].popover(str(emp_row["Pending"]), use_container_width=True):
            st.markdown(f"**Pending Tasks for {emp}**")
            if task_lists[emp]["Pending"]:
                for task in task_lists[emp]["Pending"]:
                    st.markdown(f"• {task['day']} • {task['area']}: {task['action']}")
            else:
                st.write("No pending tasks")
        
        # Awaited
        with row_cols[5].popover(str(emp_row["Awaited"]), use_container_width=True):
            st.markdown(f"**Awaited Tasks for {emp}**")
            if task_lists[emp]["Awaited"]:
                for task in task_lists[emp]["Awaited"]:
                    st.markdown(f"• {task['day']} • {task['area']}: {task['action']}")
            else:
                st.write("No awaited tasks")
        
        # Not Applicable
        with row_cols[6].popover(str(emp_row["Not Applicable"]), use_container_width=True):
            st.markdown(f"**Not Applicable Tasks for {emp}**")
            if task_lists[emp]["Not Applicable"]:
                for task in task_lists[emp]["Not Applicable"]:
                    st.markdown(f"• {task['day']} • {task['area']}: {task['action']}")
            else:
                st.write("No not applicable tasks")
        
        # Progress (%)
        row_cols[7].markdown(f"{emp_row['Progress (%)']}%")
        
        st.divider()
    
    # Filters row
    st.markdown("#### 🔎 Filters")
    filter_col1, filter_col2, filter_col3, reset_col = st.columns([2, 2, 2, 1])
    with filter_col1:
        st.selectbox("Week", ["All", "Week 0", "Week 1", "Week 2", "Week 3", "Week 4"], index=0)
    with filter_col2:
        st.selectbox("Status", ["All", "Pending", "In Progress", "Done", "Awaited"], index=0)
    with filter_col3:
        st.selectbox("Priority", ["All", "High", "Medium", "Low"], index=0)
    with reset_col:
        st.button("Reset Filters", use_container_width=True)
    
    st.write("")
    
    # Main content grid
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Pending Tasks
        st.markdown("#### ⚠️ Pending Tasks")
        all_day_labels = sorted(list(set([act["day"] for act in activities if act["day"] is not None])))
        day_options = ["All Weeks/Days"] + all_day_labels
        selected_day = st.selectbox("Select Week/Day", day_options, key="pending_day")
        
        filtered_activities = activities if selected_day == "All Weeks/Days" else [act for act in activities if act["day"] == selected_day]
        
        pending_data = []
        for emp in filtered_employee_names:
            emp_state = state.get(emp, {})
            emp_pending = []
            for act in filtered_activities:
                act_id = str(act["id"])
                task_data = emp_state.get(act_id, {})
                status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
                if status in ["Pending", "Awaited"]:
                    emp_pending.append(f"{act['day']} • {act['area']}: {act['action']}")
            if emp_pending:
                pending_data.append({
                    "Employee": emp,
                    "Pending Tasks": len(emp_pending),
                    "Task Details": emp_pending
                })
        
        if pending_data:
            for item in pending_data:
                with st.expander(f"{item['Employee']} – {item['Pending Tasks']} Pending Tasks", expanded=False):
                    for task in item['Task Details']:
                        st.markdown(f"• {task}")
        else:
            st.info(f"All {selected_day} tasks are completed! 🎉")
    
    with col2:
        # Charts
        st.markdown("#### 📊 Progress Overview")
        
        # Task Completion Pie Chart
        task_status_counts = {
            "Done": completed_tasks,
            "In Progress": in_progress_tasks,
            "Pending": pending_tasks,
            "Not Applicable": total_tasks - completed_tasks - in_progress_tasks - pending_tasks
        }
        df_pie = pd.DataFrame(list(task_status_counts.items()), columns=["Status", "Count"])
        fig_pie = px.pie(df_pie, values="Count", names="Status", title="Task Completion", color_discrete_map={
            "Done": "#22C55E",
            "In Progress": "#F59E0B",
            "Pending": "#EF4444",
            "Not Applicable": "#9CA3AF"
        })
        fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.write("")
        
        # BLK Credentials
        st.markdown("#### 📋 BLK Credentials & Start Dates")
        cols_cred = st.columns(1)
        
        # Find employee name column (try various names)
        emp_name_col = None
        for col in df_resources.columns:
            col_lower = str(col).lower()
            if "vlinker" in col_lower or "employee" in col_lower or "name" in col_lower:
                emp_name_col = col
                break
        
        # Find credential date column (try various names)
        cred_col = None
        for col in df_resources.columns:
            col_lower = str(col).lower()
            if "credential" in col_lower or "blk" in col_lower or "received" in col_lower:
                cred_col = col
                break
        
        df_resources_normalized = df_resources.copy()
        if emp_name_col:
            df_resources_normalized["emp_normalized"] = df_resources_normalized[emp_name_col].astype(str).str.strip().str.replace("*", "", regex=False).str.lower()
        
        for emp in filtered_employee_names:
            emp_normalized = emp.strip().replace("*", "").lower()
            emp_row = None
            if emp_name_col:
                emp_row = df_resources_normalized[df_resources_normalized["emp_normalized"] == emp_normalized]
            
            cred_date = "Not Received"
            if emp_row is not None and len(emp_row) > 0 and cred_col:
                cd = emp_row.iloc[0][cred_col]
                if pd.notna(cd):
                    if isinstance(cd, (int, float)):
                        cred_date = f"Day {int(cd)}"
                    else:
                        cred_date = str(cd)
            if cred_date == "Not Received":
                blk_task_status = employee_blk_cred_task_status.get(emp, "")
                if blk_task_status and "done" in str(blk_task_status).lower():
                    cred_date = "Received (Task Done)"
            
            start_date = employee_start_dates.get(emp, "N/A")
            start_date_str = str(start_date) if start_date is not None else "N/A"
            
            st.markdown(f"""
            <div class="card">
                <h4 style="margin:0 0 8px; color:#1F2937;">{emp}</h4>
                <p style="margin:4px 0; font-size:14px; color:#6B7280;">Start Date: {start_date_str}</p>
                <p style="margin:4px 0; font-size:14px; color:{ '#22C55E' if cred_date != 'Not Received' else '#EF4444' };">
                    Credentials: {cred_date if cred_date != 'Not Received' else '❌ Not Received'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            saved_receipt = parse_timestamp(
                sla_state["credentials_received_at"].get(emp)
            )
            with st.form(f"credential_receipt_{emp}"):
                receipt_date = st.date_input(
                    "Credential receipt date",
                    value=saved_receipt.date() if saved_receipt else date.today(),
                    key=f"credential_receipt_date_{emp}",
                )
                receipt_time = st.time_input(
                    "Credential receipt time (local)",
                    value=(
                        saved_receipt.time().replace(second=0, microsecond=0)
                        if saved_receipt
                        else datetime.now().time().replace(second=0, microsecond=0)
                    ),
                    key=f"credential_receipt_time_{emp}",
                )
                save_receipt = st.form_submit_button("Save receipt date and time")
            if save_receipt:
                sla_state["credentials_received_at"][emp] = datetime.combine(
                    receipt_date, receipt_time
                ).isoformat(timespec="minutes")
                save_sla_state(sla_state)
                st.success(f"Credential receipt time saved for {emp}.")
                st.rerun()

            employee_activities = [
                activity
                for activity in activities
                if activity_day_number(activity.get("day")) is not None
            ]
            if employee_activities:
                with st.expander(f"Day 1–5 SLA details for {emp}"):
                    for activity in employee_activities:
                        activity_task_data = state.get(emp, {}).get(
                            str(activity["id"]), {}
                        )
                        sla_label, deadline = get_activity_sla(
                            activity,
                            activity_task_data,
                            saved_receipt,
                            holiday_dates_by_employee.get(emp),
                            datetime.now(),
                        )
                        st.markdown(
                            f"**{activity['day']} — {activity['action']}**"
                        )
                        if sla_label:
                            st.markdown(
                                render_sla_status(sla_label),
                                unsafe_allow_html=True,
                            )
                        if deadline:
                            st.caption(f"Deadline: {deadline:%Y-%m-%d %H:%M}")
            st.write("")
    
    st.write("")
    st.markdown("#### 📋 All Vlink Employees")
    
    # Configure AG Grid
    gb = GridOptionsBuilder.from_dataframe(df_resources)
    gb.configure_pagination(paginationPageSize=10, paginationAutoPageSize=False)  # Enable pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_default_column(
        editable=True,  # Make columns editable
        resizable=True,  # Make columns resizable
        sortable=True,  # Make columns sortable
        filterable=True  # Make columns filterable
    )
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    grid_options = gb.build()
    
    # Display AG Grid
    grid_response = AgGrid(
        df_resources,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=True,
        theme="alpine",  # You can try "balham", "material", "streamlit", "alpine"
        height=400,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True
    )
    
    # Save changes back to Excel
    if st.button("💾 Save Changes to Excel", type="primary"):
        try:
            # Get the modified DataFrame from grid
            modified_df = grid_response['data']
            
            # Load the existing workbook
            wb = load_workbook(DATA_PATH_DEFAULT)
            ws = wb["Resource List"]
            
            # Get headers from the sheet (row 2, since the data starts at row 3)
            headers = [cell.value for cell in ws[2]]
            
            # Update the sheet with modified data
            for idx, row in modified_df.iterrows():
                # idx in df is 0-based, sheet rows start at 3 (row 2 is headers)
                sheet_row = idx + 3
                for col_idx, header in enumerate(headers):
                    if header in row:
                        value = row[header]
                        # Handle NaN (pandas missing values) by setting to None
                        if pd.isna(value):
                            value = None
                        ws.cell(row=sheet_row, column=col_idx + 1, value=value)
            
            # Save the workbook
            wb.save(DATA_PATH_DEFAULT)
            
            st.success("✅ Changes saved successfully!")
            st.cache_data.clear()  # Clear cache to reload fresh data
            st.rerun()  # Refresh the app
            
        except Exception as e:
            st.error(f"❌ Error saving changes: {str(e)}")

# ----------------------------------------------------------------------------
# Employee View
# ----------------------------------------------------------------------------
def render_employee_view(
    selected_employee, activities, state, sla_state, holiday_dates
):
    st.markdown(f"#### 📋 Onboarding Checklist for {selected_employee}")
    emp_state = state.get(selected_employee, {})
    credentials_received_at = parse_timestamp(
        sla_state["credentials_received_at"].get(selected_employee)
    )
    now = datetime.now()
    
    total = len(activities)
    completed = 0
    pending_awaited_acts = []
    display_activities = []
    for act in activities:
        act_id = str(act["id"])
        task_data = emp_state.get(act_id, {})
        status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
        if status in ["Done"]:
            completed += 1
        if status in ["Pending", "Awaited"]:
            pending_awaited_acts.append(act)
        is_day_one_to_five = activity_day_number(act.get("day")) is not None
        if status in ["Pending", "Awaited"] or is_day_one_to_five:
            display_activities.append(act)
    
    # Progress bar
    progress = completed / total if total else 0
    st.progress(progress)
    st.markdown(f"**Overall Progress**: {completed}/{total} tasks completed ({(progress * 100):.1f}%)")
    st.write("")
    
    if not pending_awaited_acts:
        st.info("🎉 All tasks are completed!")
    if not display_activities:
        return
    
    grouped_activities = {}
    for act in display_activities:
        day = act["day"] or "Uncategorized"
        if day not in grouped_activities:
            grouped_activities[day] = []
        grouped_activities[day].append(act)
    
    for day, acts in grouped_activities.items():
        pending_count = 0
        for act in acts:
            activity_data = emp_state.get(str(act["id"]), {})
            activity_status = (
                activity_data.get("status", "Pending")
                if isinstance(activity_data, dict)
                else activity_data
            )
            if activity_status in ["Pending", "Awaited"]:
                pending_count += 1
        with st.expander(f"📅 {day} ({pending_count} pending tasks)", expanded=True):
            for act in acts:
                act_id = str(act["id"])
                task_data = emp_state.get(act_id, {})
                current_status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
                current_comment = task_data.get("comment", "") if isinstance(task_data, dict) else ""
                
                # Check if this is an access-related task
                is_access_task = "verify access" in act["action"].lower() or \
                                "request access" in act["action"].lower() or \
                                "verify access" in act["area"].lower() or \
                                "request and/or verify access" in act["area"].lower()
                
                status_options = ["Pending", "In Progress", "Done", "Not Applicable", "Awaited"]
                
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{act['area']}**: {act['action']}")
                    sla_label, deadline = get_activity_sla(
                        act,
                        task_data,
                        credentials_received_at,
                        holiday_dates,
                        now,
                    )
                    if sla_label:
                        st.markdown(
                            render_sla_status(sla_label), unsafe_allow_html=True
                        )
                    if deadline:
                        st.caption(f"Deadline: {deadline:%Y-%m-%d %H:%M}")
                    if act["how_to"]:
                        with st.expander("ℹ️ How to complete this task?"):
                            st.write(act["how_to"])
                    if is_access_task:
                        with st.expander("💬 Remarks/Comments (e.g., how long this will take)"):
                            new_comment = st.text_area(
                                "Add comments about time to complete or other details",
                                value=current_comment,
                                key=f"emp_comment_{selected_employee}_{act_id}",
                                height=80
                            )
                            if new_comment != current_comment:
                                if selected_employee not in state:
                                    state[selected_employee] = {}
                                if act_id not in state[selected_employee] or not isinstance(state[selected_employee][act_id], dict):
                                    state[selected_employee][act_id] = {"status": current_status, "comment": ""}
                                state[selected_employee][act_id]["comment"] = new_comment
                                save_state(state)
                                st.success("Comment updated!")
                with c2:
                    st.markdown(render_status_badge(current_status), unsafe_allow_html=True)
                    new_status = st.selectbox(
                        "Change Status",
                        status_options,
                        index=status_options.index(current_status) if current_status in status_options else 0,
                        key=f"emp_{selected_employee}_{act_id}",
                    )
                    if new_status != current_status:
                        if selected_employee not in state:
                            state[selected_employee] = {}
                        if act_id not in state[selected_employee] or not isinstance(state[selected_employee][act_id], dict):
                            state[selected_employee][act_id] = {"status": new_status, "comment": current_comment}
                        else:
                            state[selected_employee][act_id]["status"] = new_status
                        if new_status == "Done":
                            state[selected_employee][act_id]["completed_at"] = (
                                datetime.now().isoformat(timespec="seconds")
                            )
                        else:
                            state[selected_employee][act_id].pop("completed_at", None)
                        save_state(state)
                        st.success("Status updated!")

# ----------------------------------------------------------------------------
# Build Notifications
# ----------------------------------------------------------------------------
def build_notifications(role, selected_emp, state, emp_list, activities):
    notes = []
    if role == "Project Manager":
        pending_count = 0
        total_count = 0
        for emp in emp_list:
            emp_state = state.get(emp, {})
            for act in activities:
                total_count += 1
                act_id = str(act["id"])
                task_data = emp_state.get(act_id, {})
                status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
                if status in ["Pending", "Awaited"]:
                    pending_count += 1
        notes.append((f"📊 Overall progress: {total_count - pending_count}/{total_count} tasks completed", False))
    elif role == "Employee" and selected_emp:
        emp_state = state.get(selected_emp, {})
        pending = 0
        for act in activities:
            act_id = str(act["id"])
            task_data = emp_state.get(act_id, {})
            status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
            if status in ["Pending", "Awaited"]:
                pending += 1
        notes.append((f"✅ You have {len(activities) - pending}/{len(activities)} tasks completed", False))
    return notes

# ----------------------------------------------------------------------------
# Export
# ----------------------------------------------------------------------------
def render_export(state, employee_names, activities, df_resources):
    st.markdown("---")
    st.markdown("#### 📤 Export Report")
    
    def build_export_bytes(state_dict):
        buffer = io.BytesIO()
        
        # Build pending tasks data
        pending_data = []
        for emp in employee_names:
            emp_state = state_dict.get(emp, {})
            for act in activities:
                act_id = str(act["id"])
                task_data = emp_state.get(act_id, {})
                status = task_data.get("status", "Pending") if isinstance(task_data, dict) else task_data
                comment = task_data.get("comment", "") if isinstance(task_data, dict) else ""
                
                if status in ["Pending", "Awaited"]:
                    pending_data.append({
                        "Employee": emp,
                        "Day/Week": act["day"],
                        "Area": act["area"],
                        "Task/Action": act["action"],
                        "How To Complete": act["how_to"],
                        "Status": status,
                        "Remarks/Comments": comment
                    })
        
        df_pending = pd.DataFrame(pending_data)
        
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_pending.to_excel(writer, sheet_name="Pending Tasks", index=False)
            df_resources.to_excel(writer, sheet_name="Resource List", index=False)
        
        # Seek to the beginning of the buffer before returning
        buffer.seek(0)
        return buffer.getvalue()
    
    st.download_button(
        label="⬇️ Download Pending Tasks Report",
        data=build_export_bytes(state),
        file_name=f"BLK_Pending_Tasks_{datetime.today().date()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    df_resources, activities, employee_names, employee_initial_status, employee_start_dates, employee_blk_cred_task_status = load_all_blk_data()
    state = load_state(employee_initial_status)
    sla_state = load_sla_state()
    holiday_dates_by_employee = {}
    holiday_dates_by_year = {}
    for emp, timestamp in sla_state["credentials_received_at"].items():
        if emp not in employee_names:
            continue
        received_at = parse_timestamp(timestamp)
        if received_at is None:
            continue
        required_years = [received_at.year]
        if received_at.month == 12 and received_at.day >= 22:
            required_years.append(received_at.year + 1)
        employee_holidays = set()
        calendar_unavailable = False
        for year in required_years:
            if year not in holiday_dates_by_year:
                try:
                    holiday_dates_by_year[year] = load_yearly_holiday_dates(year)
                except (PyMongoError, ValueError):
                    logger.exception(
                        "Unable to load yearly_holiday records for SLA year %s.",
                        year,
                    )
                    holiday_dates_by_year[year] = None
            year_holidays = holiday_dates_by_year[year]
            if year_holidays is None:
                calendar_unavailable = True
            else:
                employee_holidays.update(year_holidays)
        holiday_dates_by_employee[emp] = (
            None if calendar_unavailable else employee_holidays
        )

    if any(value is None for value in holiday_dates_by_employee.values()):
        st.error(
            "Some SLA statuses are unavailable because the yearly holiday "
            "calendar could not be loaded for one or more credential receipt "
            "years. Check MONGODB_URL, MONGODB_DATABASE, and yearly_holiday."
        )
    
    role, selected_employee, filtered_employee_names = render_sidebar(df_resources, employee_names)
    notifications = build_notifications(role, selected_employee, state, filtered_employee_names, activities)
    
    render_header(notifications)
    
    if role == "Employee" and selected_employee:
        render_employee_view(
            selected_employee,
            activities,
            state,
            sla_state,
            holiday_dates_by_employee.get(selected_employee),
        )
    else:
        render_pm_dashboard(
            filtered_employee_names,
            activities,
            state,
            df_resources,
            employee_start_dates,
            employee_blk_cred_task_status,
            sla_state,
            holiday_dates_by_employee,
        )
    
    render_export(state, employee_names, activities, df_resources)

if __name__ == "__main__":
    main()
