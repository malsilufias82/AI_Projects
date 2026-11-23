RULES = {
    "leave_patterns": [
        r'\bleave\b',
        r'\bon leave\b',
        r'\bon planned leave\b',
        r'\bsick leave\b',
        r'\bLEAVE\b',
        r'\bOn Leave\b',
        r'\bOn planned leave\b',
        r'\bSick leave\b'
    ],
    "template_patterns": [
        r'Your Name\s*',
        r'✅\s*(Today\'s Activities|Work Completed Today|Work Completed on \w+)?\s*:?\s*',
        r'🔄\s*Work in Progress\s*:?\s*',
        r'⏳\s*Planned for (Tomorrow|Next Working Day)\s*:?\s*',
        r'🚧\s*Blockers / Support Needed / Impact( of the blocker)?\s*:?\s*',
        r'📝\s*Additional Notes\s*:?\s*',
        r'✅ Work Completed Today\s*:\s*',
        r'🔄 Work in Progress\s*:\s*',
        r'⏳ Planned for Tomorrow\s*:\s*',
        r'🚧 Blockers.*?📝 Additional Notes\s*:\s*',
        r'📝 Additional Notes\s*:\s*',
    ],
    "name_headers": [
        'team member name', 'member name', 'employee name', 'emp name',
        'vlinker', 'vlinkers', 'name', 'emp. name'
    ],
    "day_names_short": [
        'Mon', 'Tue', 'Wed', 'Thu', 'Fri'
    ]
    
}

SHEET_CONFIG = {
    "access_gate": {
        "sheet_name_patterns": [
            r"access.*?gate",
            r"accessgate",
            r"access.*?api",
            r"access\s*gate.*?standup.*?status\.xlsx"
        ],
        "column_employee_name": {
            "index": 1,
        },
        "column_week_days": {
            "index_start": 3,
            "index_end": 7
        },
        "row_column_name": {
            "index": 0
        }
    },
    "bud_db": {
        "sheet_name_patterns": [
            r"data.*?team",
            r"daily.*?tracker",
            r"data\s*team.*?daily\s*tracker.*?\.xlsx"
        ],
        "column_employee_name": {
            "index": 2,
        },
        "column_team_lead": {
            "index": 3,
        },
        "column_week_days": {
            "index_start": 5,
            "index_end": 9
        },
        "row_column_name": {
            "index": 2
        }
    },
    "dexia": {
        "sheet_name_patterns": [
            r"dexia",
            r"dexia.*?standup"
        ],
        "column_employee_name": {
            "index": 0,
        },
        "column_week_days": {
            "index_start": 2,
            "index_end": 6
        },
        "row_column_name": {
            "index": 0
        },
        "sheet_type": "row_based"
    },
    "phoenix_product": {
        "sheet_name_patterns": [
            r"phoenix.*?product.*?team",
            r"product.*?team"
        ],
        "column_employee_name": {
            "index": 3,
        },
        "column_team_lead": {
            "index": 4,
        },
        "column_week_days": {
            "index_start": 10,
            "index_end": 14
        },
        "row_column_name": {
            "index": 2
        }
    },
    "phoenix_platform": {
        "sheet_name_patterns": [
            r"phoenix.*?platform.*?team",
            r"platform.*?team"
        ],
        "column_employee_name": {
            "index": 1,
        },
        "column_week_days": {
            "index_start": 7,
            "index_end": 11
        },
        "sheet_type": "column_based",
        "row_column_name": {
            "index": 1
        }
    },
    "ptr": {
        "sheet_name_patterns": [
            r"ptr",
            r"ptr.*?standup"
        ],
        "column_employee_name": {
            "index": 0,
        },
        "sheet_type": "row_based",

        "column_week_days": {
            "index_start": 2,
            "index_end": 6
        },
        "row_column_name": {
            "index": 1
        },
    },
    "pmi": {
        "sheet_name_patterns": [
            r"pmi",
            r"pmi.*?status"
        ],
        "column_employee_name": {
            "index": 0,
        },
        "column_week_days": {
            "index_start": 2,
            "index_end": 6
        },
        "sheet_type": "row_based",
        "row_column_name": {
            "index": 0
        }
    },
}
