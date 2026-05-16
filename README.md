# AI Travel Assistant

Vacation planner backend for class: FastAPI, SQLAlchemy, JWT, trips, itineraries. After a trip or itinerary is saved, a small audit line is written in the background (logging).

## Run it

Python 3.11+ (3.12 is fine). From the repo root:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Fill in `.env` — you need at least `DATABASE_URL` and `JWT_SECRET_KEY`. For local work, SQLite is enough (`sqlite:///./ai_travel_assistant.db` is in `.env.example`). Postgres works too if you change the URL; `psycopg` is already in `requirements.txt`.

Start the server:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/docs** to try the API (Swagger). Health check: `GET /health`.

## Tests

```bash
python -m pytest -q
```

## Layout

Routers live under `app/routers/`, Pydantic models under `app/schemas/`, tables under `app/models/`, config and DB under `app/core/`, shared auth dependency in `app/deps.py`. `app/services/` holds the audit helper the trip/itinerary routes schedule with `BackgroundTasks`.

Tables are created on startup (`create_all` in `app/main.py`); there are no migrations in this repo.

`POST /trips` and `POST /itineraries` responses include a `message` field like in the assignment examples; other shapes are easiest to check in `/docs`.
