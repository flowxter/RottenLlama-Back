import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
import os
from dotenv import load_dotenv

# Cargar variables de entorno para pruebas
load_dotenv(dotenv_path='tests/.env.test')

TEST_PASSWORD = os.getenv('TEST_PASSWORD')

User = get_user_model()

@pytest.mark.django_db
def test_send_reset_email_to_existing_user():
    client = APIClient()
    email = "testuser@example.com"
    password = TEST_PASSWORD
    username = "testuser"
    User.objects.create_user(email=email, username=username,password=password)
    
    url = reverse("reset-password")
    response = client.post(url, {"email": email})
    
    assert response.status_code == 200
    assert "message" in response.data


@pytest.mark.django_db
def test_send_reset_email_to_nonexistent_user():
    client = APIClient()
    url = reverse("reset-password")
    response = client.post(url, {"email": "nonexistent@example.com"})
    
    assert response.status_code == 400
    assert "email" in response.data

@pytest.mark.django_db
def test_reset_password_nonexistent_email(client):
    # Email no registrado
    response = client.post('/api/auth/reset-password/', {
        'email': 'nonexistent@example.com'
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
