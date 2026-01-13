# Vertigo Games – Clan Management API

This project is a lightweight backend service for managing **clans** in a game environment.  
It is built as part of the Vertigo Games Data Engineer case study.

The service exposes a REST API to:
- Create a clan
- List clans
- Search clans by name
- Delete a clan

All responses are returned in **JSON** format.

---

## Tech Stack

- **Python 3.12**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy (async)**
- **Docker**
- **Uvicorn**

---

## Data Model

### Clan

| Field        | Type      | Description |
|-------------|----------|-------------|
| `id`        | UUID     | Unique clan identifier |
| `name`      | string   | Clan name |
| `region`    | string   | Region code (e.g. `TR`, `US`) |
| `created_at`| datetime | Creation timestamp (UTC) |

The database enforces:
- UUID primary keys
- UTC timestamps
- Required `name` and `region` fields

---

## Environment Variables

The application expects the following environment variables:

```bash
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=clans_db
PORT=8080

# Running the Project

Build image
docker build -t clan-api .

Run container (macOS / Windows)
docker run --rm -p 8080:8080 \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_NAME=clans_db \
  -e PORT=8080 \
  clan-api


