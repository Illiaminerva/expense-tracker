import pytest

def test_app_creation(app):
    """Test that the app can be created."""
    assert app is not None
    assert app.testing

def test_client_creation(client):
    """Test that the client can be created."""
    assert client is not None
    
def test_home_page_redirects_to_login(client):
    """Test that the home page redirects to login when not authenticated."""
    response = client.get('/')
    assert response.status_code == 302  # Redirect status code
    
    # Follow the redirect
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

def test_login_page_accessible(client):
    """Test that the login page is directly accessible."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_register_page_accessible(client):
    """Test that the register page is directly accessible."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_nonexistent_route_returns_404(client):
    """Test that a nonexistent route returns a 404 status code."""
    response = client.get('/nonexistent-route')
    assert response.status_code == 404 