# Zenith

A full-stack AI-based Project Evaluation Platform built with FastAPI and Quasar.

---

## Overview

Zenith is a production-ready application for managing project evaluations. It consists of a FastAPI backend, a Quasar/Vue frontend, and supporting services (PostgreSQL, MongoDB, Redis, Celery workers) orchestrated with Docker Compose.

---

## Repository Structure

```
zenith/
├── backend/          # FastAPI backend API and worker services
├── frontend/         # Quasar (Vue 3) frontend
├── onboarding_dashboard/  # Onboarding dashboard module
├── status_report_bot/     # Status reporting automation bot
├── pages.json        # Page definitions
└── README.md         # This file
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Python 3.11) |
| Frontend Framework | Quasar (Vue 3) + Vite |
| Relational DB | PostgreSQL 15 |
| Document DB | MongoDB 7 |
| Cache / Task Broker | Redis |
| Task Queue | Celery |
| Containerization | Docker + Docker Compose |

---

## Quick Start (Docker)

1. Copy the backend `.env.example` to `.env` and update values as needed:

```bash
cp backend/.env.example backend/.env
```

Key variables to set:

- `DATABASE_URL` — PostgreSQL connection string
- `MONGODB_URL` — MongoDB connection string
- `REDIS_URL` — Redis connection string
- `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` — Celery broker and result backend

2. Navigate to the backend directory where `docker-compose.yml` is located:

```bash
cd backend/
```

3. Build and start all services:

```bash
sudo docker compose up --build
```

4. Access the services:

- **Frontend (Quasar dev server):** http://localhost:8101
- **Backend API (FastAPI):** http://localhost:8100
- **pgAdmin (if enabled):** http://localhost:5050

---

## Services (Docker Compose)

| Service | Description | Exposed Port |
|---|---|---|
| `api` | FastAPI application | `8100` |
| `worker` | Celery background worker | — |
| `frontend` | Quasar Vite dev server | `8101` |
| `db` | PostgreSQL 15 | `5433` |
| `mongodb` | MongoDB 7 | `27017` |
| `redis` | Redis 7 | `6380` |
| `pgadmin` | pgAdmin web UI | `5050` |

---

## Notes

- The backend and frontend communicate through the `zenith_net` Docker network.
- The frontend `quasar.config.js` proxy targets `http://localhost:8100` by default for local development.
- This repository uses pnpm for the frontend and pip for the Python backend.
