# Project 01 — Optical Sales API (Python / FastAPI / SQLite)

An original API demo for a fictional optical retailer. Demonstrates clean HTTP endpoints, input validation, money stored as integer cents, SQLite foreign keys, parameterized SQL, dependency injection and API integration tests.

## Run

```bash
python -m pip install -r requirements.txt
API_KEY=change-this-key uvicorn app.main:app --reload
python -m pytest -q
```

Windows PowerShell: `$env:API_KEY="change-this-key"; uvicorn app.main:app --reload`

Visit `http://127.0.0.1:8000/docs`. Use `X-API-Key: change-this-key` in protected requests. Example:

```bash
curl -X POST http://127.0.0.1:8000/salespeople -H 'Content-Type: application/json' -H 'X-API-Key: change-this-key' -d '{"name":"Ana","monthly_target":"1200.00"}'
```

## Endpoints

- `GET /health` — public health response
- `POST /salespeople` — create salesperson, authenticated
- `POST /orders` — create an order for an existing salesperson, authenticated
- `GET /reports/sales` — total sales, target attainment, order count

## Design decisions

- Monetary amounts are stored as **integer cents** to avoid floating-point rounding errors.
- Inputs use Pydantic constraints and validation; foreign key mistakes return HTTP 404.
- SQL uses parameter binding to mitigate injection; FK enforcement is explicit.
- Zero targets produce `null` attainment instead of division by zero.
- Tests inject a private in-memory database, isolating runs.

## Known limitations / production roadmap

- API key authentication is a demo only (default key is insecure and must never be used in production).
- SQLite and one shared connection are suitable for a portfolio demo, not concurrent production traffic; use PostgreSQL and a managed connection pool.
- Add role-based authorization, pagination, audit logging, time-window filters, secrets management, migrations, and CI.
- Order changes and returns/refunds are intentionally out of scope.

**Not affiliated with any real clinic or business; no real client data.**
