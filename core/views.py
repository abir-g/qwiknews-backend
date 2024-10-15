from django.shortcuts import render

# accounts/views.py

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

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
                secure=settings.SESSION_COOKIE_SECURE,  # This will be False in development
                samesite=settings.SESSION_COOKIE_SAMESITE,  # This will be 'Lax' or 'None'
                max_age=60*60*24*7,  # Expiry for the cookie (7 days in this example)
                domain='localhost',  # Explicitly set for localhost
                path='/',  # Ensure the cookie is sent for all paths
            )

            # Remove refresh token from response body for security
            del response.data['refresh']

        return response

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Check if refresh token is in the cookie
        refresh_token = request.COOKIES.get('refresh_token')

        # If not in cookie, check the request body
        if not refresh_token:
            refresh_token = request.data.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token
        else:
            return Response({"detail": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            return super().post(request, *args, **kwargs)
        except TokenError as e:
            raise InvalidToken(e.args[0])
