import pytest
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def logged_in_client(client):
    # Register a user
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    return client

def test_index_page(client):
    """Test that the index page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Flask App' in response.data

def test_user_registration(client):
    """Test user registration"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data

def test_user_login(client):
    """Test user login"""
    # First register
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Then login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Logged in successfully' in response.data

def test_profile_requires_login(client):
    """Test that profile page requires login"""
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_profile_edit(logged_in_client):
    """Test profile editing functionality"""
    response = logged_in_client.post('/profile', data={
        'first_name': 'John',
        'last_name': 'Doe',
        'display_name': 'JohnnyD',
        'city': 'New York',
        'state': 'NY',
        'country': 'USA'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Profile updated successfully' in response.data
    assert b'John' in response.data
    assert b'Doe' in response.data
    assert b'JohnnyD' in response.data
    assert b'New York' in response.data
    assert b'NY' in response.data
    assert b'USA' in response.data

def test_profile_shows_current_data(logged_in_client):
    """Test that profile page shows current user data"""
    # Update profile
    logged_in_client.post('/profile', data={
        'first_name': 'Jane',
        'last_name': 'Smith',
        'display_name': 'JSmith',
        'city': 'Los Angeles',
        'state': 'CA',
        'country': 'USA'
    })
    
    # Get profile page
    response = logged_in_client.get('/profile')
    assert response.status_code == 200
    assert b'Jane' in response.data
    assert b'Smith' in response.data
    assert b'JSmith' in response.data
    assert b'Los Angeles' in response.data
    assert b'CA' in response.data

def test_profile_partial_update(logged_in_client):
    """Test that profile can be partially updated"""
    # Update only some fields
    response = logged_in_client.post('/profile', data={
        'first_name': 'Bob',
        'last_name': '',
        'display_name': '',
        'city': 'Seattle',
        'state': '',
        'country': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Profile updated successfully' in response.data
    assert b'Bob' in response.data
    assert b'Seattle' in response.data
