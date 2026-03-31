# LDWS Backend

## Project convention
- ORM models are only for application-facing table mapping and CRUD/auth logic. 
TimescaleDB-specific database features (hypertables, triggers, compression, retention, continuous aggregates) 
are managed at the database/SQL bootstrap layer and are not re-implemented in backend ORM models.
- Database bootstrap SQL is the source of truth for TimescaleDB-specific features.

## Run
uv sync
uv run uvicorn app.main:app --reload