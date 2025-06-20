from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['username'] = user.username
#         return token

#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token["username"] = user.username  # Add username to token payload
#         return token

#     def validate(self, attrs):
#         # Replace 'username' with 'email' for authentication
#         attrs["username"] = attrs.get("email")
#         return super().validate(attrs)
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        # Autenticamos usando el email
        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        # Obtenemos los tokens con el usuario autenticado
        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
        }

#Logica para recuperacion de password
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            # Puedes hacer algo con el usuario aquí si lo necesitas
            # Por ejemplo, verificar si está activo:
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")

    def send_reset_email(self, request):  # Asegúrate de pasar el 'request' aquí
        email = self.validated_data["email"]
        user = User.objects.get(email=email)

        # Generar un token aleatorio
        token = get_random_string(length=32)

        # Guardar el token en el usuario
        user.reset_password_token = token
        user.save()

        # Construir el enlace con el token (sin el dominio)
        reset_url = reverse('password_reset_confirm', args=[token])

        # Obtener el dominio completo (por ejemplo: localhost:8000)
        domain = get_current_site(request).domain

        # Usa HTTPS dinámicamente basado en la solicitud
        protocol = 'https' if request.is_secure() else 'http'
        full_url = f"{protocol}://{domain}{reset_url}"

        # Enviar el correo con el enlace para restablecer la contraseña
        subject = "Instructions to Reset Your Password"
        message = f"""
Hello {user.username},

We have received a request to reset the password for your SpittinLlama account. 
If you did not request this change, please ignore this email.

To reset your password, simply click the link below:

{full_url}

This link will expire in 24 hours, so be sure to use it before then.
If you have any issues or questions, feel free to contact us.
Thank you for using RottenLlama!

Best regards,
The SpittinLlama Team
"""
        send_mail(
            subject,
            message,
            'no-reply@tuapp.com',  # Desde qué correo se enviará
            [email],  # El destinatario
            fail_silently=False,
        )

        

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data