from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    clients,
    daily_reports,
    emails,
    health,
    holidays,
    permissions,
    projects,
    roles,
    sheets,
    users,
    week0,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(sheets.router, prefix="/sheets", tags=["Sheets"])
api_router.include_router(daily_reports.router, prefix="/daily-reports", tags=["Daily Reports"])
api_router.include_router(emails.router, prefix="/emails", tags=["Emails"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(week0.router, prefix="/week0", tags=["Week0"])
api_router.include_router(holidays.router, prefix="/holidays", tags=["Holidays"])
