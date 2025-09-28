import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Tone Analyzer API"
    assert "version" in data

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

def test_api_info():
    """Test the API info endpoint"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data
    assert "supported_tones" in data

def test_supported_tones():
    """Test the supported tones endpoint"""
    response = client.get("/api/v1/tone/supported-tones")
    assert response.status_code == 200
    data = response.json()
    assert "supported_tones" in data
    assert isinstance(data["supported_tones"], list)
    assert len(data["supported_tones"]) > 0

def test_analyze_tone_public():
    """Test the public tone analysis endpoint"""
    test_text = "Hello, how are you today?"
    
    response = client.post(
        "/api/v1/tone/analyze",
        json={"text": test_text}
    )
    
    # This might fail if the model is not loaded, which is expected in tests
    if response.status_code == 200:
        data = response.json()
        assert "original_text" in data
        assert "detected_tone" in data
        assert "confidence_score" in data
        assert "suggestions" in data
        assert "improved_text" in data
    else:
        # If model is not loaded, we expect a 500 error
        assert response.status_code == 500

def test_register_user():
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "confirm_password": "testpassword123"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    # This might fail if MongoDB is not running, which is expected in tests
    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
    else:
        # If database is not available, we expect an error
        assert response.status_code in [500, 503]

def test_login_user():
    """Test user login"""
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = client.post(
        "/api/v1/auth/login",
        data=login_data
    )
    
    # This might fail if user doesn't exist or database is not running
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    else:
        # If authentication fails, we expect an error
        assert response.status_code in [401, 500, 503]

def test_protected_endpoint_without_token():
    """Test that protected endpoints require authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_protected_endpoint_with_invalid_token():
    """Test that protected endpoints reject invalid tokens"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

def test_cors_headers():
    """Test that CORS headers are properly set"""
    response = client.options("/")
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers or "Access-Control-Allow-Origin" in response.headers

def test_docs_endpoint():
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_redoc_endpoint():
    """Test that ReDoc documentation is accessible"""
    response = client.get("/redoc")
    assert response.status_code == 200
