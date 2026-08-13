# Week 1 – Flask CRUD App (Containerized)

Part of the 4-Week Mid-Level Cloud Engineering Project: *Design and Deploy a
Scalable 3-Tier Containerized Application on AWS Using Terraform & CI/CD*.

This is the **application layer** — a small Flask CRUD API backed by
PostgreSQL, containerized with Docker. In later weeks this image gets
deployed onto EC2 behind an Application Load Balancer, provisioned entirely
with Terraform.

## Stack
- Python 3.12 / Flask
- Flask-SQLAlchemy (ORM)
- PostgreSQL 16
- Gunicorn (production WSGI server)
- Docker + Docker Compose (local dev)

## Endpoints

| Method | Path            | Description          |
|--------|-----------------|-----------------------|
| GET    | `/`             | HTML frontend (add/list/edit/delete items in the browser) |
| GET    | `/health`       | Health check (used by the ALB later) |
| GET    | `/items`        | List all items       |
| GET    | `/items/<id>`   | Get one item          |
| POST   | `/items`        | Create an item (`{"name": "...", "description": "..."}`) |
| PUT    | `/items/<id>`   | Update an item        |
| DELETE | `/items/<id>`   | Delete an item        |

## Running locally with Docker Compose

This spins up the Flask app **and** a Postgres container together —
no local Postgres install needed.

```bash
docker compose up --build
```

Then either open **http://localhost:5000/** in your browser to use the app
directly, or test the API with curl:

```bash
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "description": "hello"}'

curl http://localhost:5000/items
```

## Project structure

```
week1-app/
├── app.py              # Flask app: routes, model, frontend route
├── templates/
│   └── index.html      # Browser UI (add/list/edit/delete items)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── .gitignore
```

Stop everything with `docker compose down` (add `-v` to also wipe the
database volume).

## Environment variables

Copy `.env.example` to `.env` and adjust if needed. Docker Compose already
sets sane defaults for local dev (see `docker-compose.yml`); these variables
matter more once the app talks to a real RDS instance in Week 2+.

| Variable      | Default    | Notes |
|---------------|------------|-------|
| `DB_USER`     | `postgres` | |
| `DB_PASSWORD` | `postgres` | Will move to AWS Parameter Store in Week 4 |
| `DB_HOST`     | `db`       | Docker Compose service name locally; RDS endpoint later |
| `DB_PORT`     | `5432`     | |
| `DB_NAME`     | `appdb`    | |

## Building and pushing the image to Docker Hub

```bash
docker build -t <your-dockerhub-username>/week1-app:latest .
docker login
docker push <your-dockerhub-username>/week1-app:latest
```

## Notes / design decisions
- `gunicorn` is used instead of the Flask dev server in the container —
  the dev server isn't meant for anything beyond local debugging.
- `db.create_all()` runs on startup for simplicity in this project. A real
  production app would use migrations (e.g. Flask-Migrate/Alembic) instead.
- `/health` returns a plain 200 with no DB dependency check for now — this
  keeps it simple for the ALB health check target in Week 2; DB
  connectivity failures will surface via the CRUD endpoints themselves.
