# ReefConnect

ReefConnect is a social media platform for scuba divers to log dives, track and share experiences
and species discoveries, and connect with the diving community.

NOTE: This is a learning project focused on building a scalable, production-ready full-stack
application.

## Project Structure

```
ReefConnect/
├── designs/          # System design documents
├── frontend/         # React + TypeScript frontend
└── backend/          # Python backend
    ├── api_service/              # FastAPI API service
    ├── common/                   # Shared utilities and classes
    ├── materialized_data_worker/ # Data aggregation worker
    ├── media_worker/             # Media processing worker
    └── ml_tagger_worker/         # ML species tagging worker
```

## Getting Started

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
# Coming soon - FastAPI + PostgreSQL setup
# Will include: virtual environment, dependencies, database migrations
```

### Development Tools

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests and linting (requires nox)
pip install nox
nox               # Run default sessions (lint + test)
nox -s test       # Run tests only
nox -s fix        # Auto-fix linting issues
```

## Features

- 🤿 Dive Log Management
- 📸 Media Gallery
- 🐠 Species Database (ScubaDex)
- 📊 Dive Statistics
- 👥 Social Connections
- 🏆 Leaderboards & Badges

## Tech Stack

**Frontend:**
- React + TypeScript
- Vite
- TailwindCSS
- shadcn/ui components

**Backend:**
- Python
- FastAPI
- PostgreSQL
- Docker
