import pytest
import os
from django.urls import reverse
from users.models import CustomUser
from rest_framework.test import APIClient
from rest_framework import status
from dotenv import load_dotenv

# Cargar variables de entorno para pruebas
load_dotenv(dotenv_path='tests/.env.test')

TEST_PASSWORD = os.getenv('TEST_PASSWORD')

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": TEST_PASSWORD
    }

@pytest.fixture
def register_url():
    return reverse('register')

@pytest.fixture
def login_url():
    return reverse('token_obtain_pair')

@pytest.fixture
def refresh_url():
    return reverse('token_refresh')

@pytest.mark.django_db
def test_user_registration(api_client, user_data, register_url):
    response = api_client.post(register_url, user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(email=user_data["email"]).exists()

@pytest.mark.django_db
def test_login_with_valid_credentials(api_client, user_data, register_url, login_url):
    api_client.post(register_url, user_data)
    response = api_client.post(login_url, {
        "email": user_data["email"],
        "password": user_data["password"]
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data

@pytest.mark.django_db
def test_login_with_invalid_credentials(api_client, login_url):
    response = api_client.post(login_url, {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_refresh_token(api_client, user_data, register_url, login_url, refresh_url):
    api_client.post(register_url, user_data)
    login_response = api_client.post(login_url, {
        "email": user_data["email"],
        "password": user_data["password"]
    })
    refresh = login_response.data["refresh"]
    response = api_client.post(refresh_url, {"refresh": refresh})
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data

@pytest.mark.django_db
def test_register_duplicate_email(api_client, user_data, register_url):
    api_client.post(register_url, user_data)
    response = api_client.post(register_url, user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data

@pytest.mark.django_db
def test_register_missing_fields(api_client, register_url):
    response = api_client.post(register_url, {
        "email": "",
        "username": "",
        "password": ""
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert "username" in response.data
    assert "password" in response.data

@pytest.mark.django_db
def test_register_does_not_return_password(api_client, user_data, register_url):
    response = api_client.post(register_url, user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert "password" not in response.data

@pytest.mark.django_db
def test_password_is_hashed(api_client, user_data, register_url):
    """Verifica que el password no se almacene en texto plano"""
    api_client.post(register_url, user_data)
    user = CustomUser.objects.get(email=user_data["email"])
    assert user.password != user_data["password"]
    assert user.check_password(user_data["password"])

@pytest.mark.django_db
def test_register_invalid_email(api_client, register_url):
    """Prueba registro con email inválido"""
    response = api_client.post(register_url, {
        "email": "notanemail",
        "username": "testuser",
        "password": TEST_PASSWORD
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_refresh_with_invalid_token(api_client, refresh_url):
    """Prueba refresh con token inválido"""
    response = api_client.post(refresh_url, {"refresh": "invalidtoken"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_refresh_with_expired_token(api_client, user_data, register_url, login_url, refresh_url):
    """Prueba refresh con token expirado (requiere configuración de tiempo corto)"""
    api_client.post(register_url, user_data)
    login_response = api_client.post(login_url, {
        "email": user_data["email"],
        "password": user_data["password"]
    })
    refresh = login_response.data["refresh"]
    
    # Simular tiempo de expiración (depende de tu configuración JWT)
    from django.utils import timezone
    from datetime import timedelta
    from rest_framework_simplejwt.tokens import RefreshToken
    
    token = RefreshToken(refresh)
    token.set_exp(from_time=timezone.now() - timedelta(days=1))
    expired_refresh = str(token)
    
    response = api_client.post(refresh_url, {"refresh": expired_refresh})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_customuser_str():
    user = CustomUser.objects.create(email='test@example.com', username='testuser')
    assert str(user) == 'testuser'

@pytest.mark.django_db
def test_create_superuser():
    user = CustomUser.objects.create_superuser(
        email='admin@example.com',
        username='admin',  # Añadir username
        password= TEST_PASSWORD
    )
    assert user.is_superuser
    assert user.is_staff
    assert user.is_active