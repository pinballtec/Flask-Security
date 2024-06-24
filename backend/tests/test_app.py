import pytest
from app import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


def test_register(client):
    response = client.post('/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '1234567890'
    })
    assert response.status_code == 200, response.data


def test_login(client):
    # Register user first
    client.post('/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '1234567890'
    })

    # Now login
    response = client.post('/signin', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200, response.data


def test_reset_password(client):
    # Register user first
    client.post('/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '1234567890'
    })

    # Now reset password
    response = client.post('/reset_password', json={
        'email': 'test@example.com',
        'old_password': 'password123',
        'new_password': 'newpassword123'
    })
    assert response.status_code == 200, response.data

    # Try to login with the new password
    response = client.post('/signin', json={
        'email': 'test@example.com',
        'password': 'newpassword123'
    })
    assert response.status_code == 200, response.data
