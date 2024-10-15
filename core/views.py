from django.shortcuts import render

# accounts/views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Call the original post method to authenticate and get access token
        response = super().post(request, *args, **kwargs)

        # Get the user object from the request after successful authentication
        if response.status_code == 200:
            # Get the refresh token from the response
            refresh_token = response.data['refresh']

            # Set the refresh token in an HttpOnly cookie
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,  # Prevent JavaScript access
                secure=settings.SESSION_COOKIE_SECURE,  # True for HTTPS
                samesite='Lax',  # Adjust SameSite policy as per your app's needs
                max_age=60*60*24*7,  # Expiry for the cookie (7 days in this example)
            )

            # Remove refresh token from response body for security
            del response.data['refresh']

        return response
