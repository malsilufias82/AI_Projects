"""
config.py
---------
Loads and validates configuration from config.json and environment
variables (.env).
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

from dotenv import load_dotenv


@dataclass
class SchedulerConfig:
    morning_time: str
    evening_time: str
    timezone: str
    holidays: List[str] = field(default_factory=list)


@dataclass
class AppConfig:
    team_excel_files: List[Dict[str, str]]
    reports_folder: str
    logs_folder: str
    data_folder: str
    skipped_employees_file: str
    scheduler: SchedulerConfig
    tenant_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    graph_scope: str = "https://graph.microsoft.com/.default"
    team_id: str = ""
    channel_id: str = ""
    requester_email: str = ""
    requester_name: str = ""
    manager_email: str = ""
    manager_name: str = ""
    pm_email: str = ""
    pm_name: str = ""
    timezone: str = "Asia/Kolkata"
    log_level: str = "INFO"
    environment: str = "development"


def load_config(config_path: str = "./config/config.json", env_path: str = "./.env") -> AppConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    load_dotenv(dotenv_path=env_path)

    with open(config_path, "r", encoding="utf-8") as f:
        raw: Dict[str, Any] = json.load(f)

    scheduler_raw = raw["scheduler"]
    scheduler = SchedulerConfig(
        morning_time=scheduler_raw["morning_time"],
        evening_time=scheduler_raw["evening_time"],
        timezone=scheduler_raw.get("timezone", "Asia/Kolkata"),
        holidays=scheduler_raw.get("holidays", [])
    )

    config = AppConfig(
        team_excel_files=raw["team_excel_files"],
        reports_folder=raw["reports_folder"],
        logs_folder=raw["logs_folder"],
        data_folder=raw.get("data_folder", "./data"),
        skipped_employees_file=raw.get("skipped_employees_file", "./data/skipped_employees.json"),
        scheduler=scheduler,
        tenant_id=os.getenv("TENANT_ID", ""),
        client_id=os.getenv("CLIENT_ID", ""),
        client_secret=os.getenv("CLIENT_SECRET", ""),
        graph_scope=os.getenv("GRAPH_SCOPE", "https://graph.microsoft.com/.default"),
        team_id=os.getenv("TEAM_ID", ""),
        channel_id=os.getenv("CHANNEL_ID", ""),
        requester_email=os.getenv("REQUESTER_EMAIL", ""),
        requester_name=os.getenv("REQUESTER_NAME", "Requester"),
        manager_email=os.getenv("MANAGER_EMAIL", ""),
        manager_name=os.getenv("MANAGER_NAME", "Manager"),
        pm_email=os.getenv("PM_EMAIL", ""),
        pm_name=os.getenv("PM_NAME", "PM"),
        timezone=os.getenv("TIMEZONE", scheduler_raw.get("timezone", "Asia/Kolkata")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        environment=os.getenv("ENVIRONMENT", "development"),
    )

    for folder in (config.reports_folder, config.logs_folder, config.data_folder):
        os.makedirs(folder, exist_ok=True)

    return config
