from datetime import datetime, timedelta
import pytest
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User

def test_login_form_display(client):
    """Test that the login form is displayed correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data

def test_register_form_display(client):
    """Test that the register form is displayed correctly"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data
    assert b'Confirm Password' in response.data

def test_protected_route_redirect(client):
    """Test that protected routes redirect to login when not authenticated"""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_login_required(client):
    """Test that protected routes require login"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Check for login indicator
    content = response.data.decode('utf-8').lower()
    assert 'budget' in content

def test_login_failure(client):
    """Test failed login attempts"""
    response = client.post('/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_logout(auth_client):
    """Test logout functionality"""
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    # Check for logout indicator
    content = response.data.decode('utf-8').lower()
    assert 'login' in content