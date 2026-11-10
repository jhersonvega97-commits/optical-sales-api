"""Minimal production-inspired sales API: validation, safe SQL, money precision and DI."""
from decimal import Decimal
import os
import sqlite3
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, status
from .db import connect, transaction
from .models import OrderCreate, OrderRead, SalespersonCreate, SalespersonRead, SalesSummary

API_KEY = os.getenv('API_KEY', 'dev-only-key')

def to_cents(value: Decimal) -> int:
    return int(value * 100)

def to_dollars(cents: int) -> Decimal:
    return (Decimal(cents) / Decimal(100)).quantize(Decimal('0.01'))

def create_app(db_path: str = ':memory:', api_key: str | None = None) -> FastAPI:
    expected_key = API_KEY if api_key is None else api_key
    db = connect(db_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        db.close()

    app = FastAPI(title='Optical Sales API', version='1.0.0', lifespan=lifespan)

    def get_db():
        return db

    def authenticate(x_api_key: str | None = Header(default=None)):
        if x_api_key != expected_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid API key')

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    @app.post('/salespeople', response_model=SalespersonRead, status_code=201, dependencies=[Depends(authenticate)])
    def add_salesperson(payload: SalespersonCreate, conn: sqlite3.Connection = Depends(get_db)):
        with transaction(conn):
            result = conn.execute('INSERT INTO salespeople(name, monthly_target_cents) VALUES (?, ?)',
                                  (payload.name, to_cents(payload.monthly_target)))
        return {'id': result.lastrowid, 'name': payload.name, 'monthly_target': payload.monthly_target}

    @app.post('/orders', response_model=OrderRead, status_code=201, dependencies=[Depends(authenticate)])
    def add_order(payload: OrderCreate, conn: sqlite3.Connection = Depends(get_db)):
        if conn.execute('SELECT 1 FROM salespeople WHERE id = ?', (payload.salesperson_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail='Salesperson not found')
        with transaction(conn):
            result = conn.execute('INSERT INTO orders(salesperson_id, customer_name, amount_cents) VALUES (?, ?, ?)',
                                  (payload.salesperson_id, payload.customer_name, to_cents(payload.amount)))
        return {'id': result.lastrowid, **payload.model_dump()}

    @app.get('/reports/sales', response_model=list[SalesSummary], dependencies=[Depends(authenticate)])
    def sales_report(conn: sqlite3.Connection = Depends(get_db)):
        rows = conn.execute("""
            SELECT s.id, s.name, s.monthly_target_cents,
                   COALESCE(SUM(o.amount_cents), 0) AS total_cents,
                   COUNT(o.id) AS order_count
              FROM salespeople s LEFT JOIN orders o ON o.salesperson_id = s.id
             GROUP BY s.id ORDER BY s.id
        """).fetchall()
        result = []
        for row in rows:
            target, total = row['monthly_target_cents'], row['total_cents']
            result.append(SalesSummary(
                salesperson_id=row['id'], salesperson_name=row['name'],
                monthly_target=to_dollars(target), total_sales=to_dollars(total),
                attainment_percent=(Decimal(total) * 100 / Decimal(target)).quantize(Decimal('.01')) if target else None,
                order_count=row['order_count']))
        return result

    return app

app = create_app(os.getenv('DATABASE_PATH', 'optical_sales.db'))
