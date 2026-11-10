import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client():
    with TestClient(create_app(':memory:', api_key='test-secret')) as client:
        yield client

@pytest.fixture
def headers():
    return {'X-API-Key': 'test-secret'}

def test_health_is_public(client):
    assert client.get('/health').json() == {'status': 'ok'}

def test_protected_routes_reject_missing_or_wrong_key(client):
    assert client.get('/reports/sales').status_code == 401
    assert client.get('/reports/sales', headers={'X-API-Key': 'wrong'}).status_code == 401

def test_create_and_report_sales(client, headers):
    salesperson = client.post('/salespeople', headers=headers, json={'name':'Ana','monthly_target':'100.00'})
    assert salesperson.status_code == 201
    identifier = salesperson.json()['id']
    for amount in ('19.99', '30.01'):
        order = client.post('/orders', headers=headers, json={
            'salesperson_id': identifier, 'customer_name': 'Customer A', 'amount': amount})
        assert order.status_code == 201
    row = client.get('/reports/sales', headers=headers).json()[0]
    assert row['order_count'] == 2
    assert row['total_sales'] == '50.00'
    assert row['attainment_percent'] == '50.00'

def test_unknown_salesperson_returns_404(client, headers):
    response = client.post('/orders', headers=headers, json={
        'salesperson_id': 999, 'customer_name': 'Customer A', 'amount': '20.00'})
    assert response.status_code == 404

def test_validation_rejects_negative_blank_and_fractional_cent(client, headers):
    assert client.post('/salespeople', headers=headers, json={
        'name': ' ', 'monthly_target': '100'}).status_code == 422
    assert client.post('/salespeople', headers=headers, json={
        'name': 'Ana', 'monthly_target': '-1'}).status_code == 422
    created = client.post('/salespeople', headers=headers, json={
        'name':'Ana','monthly_target':'0'}).json()['id']
    assert client.post('/orders', headers=headers, json={
        'salesperson_id':created, 'customer_name':'A', 'amount':'0.001'}).status_code == 422
    row = client.get('/reports/sales', headers=headers).json()[0]
    assert row['attainment_percent'] is None

def test_report_includes_people_without_orders(client, headers):
    client.post('/salespeople', headers=headers, json={'name':'Ana','monthly_target':'25.00'})
    row = client.get('/reports/sales', headers=headers).json()[0]
    assert row['total_sales'] == '0.00'
    assert row['order_count'] == 0
