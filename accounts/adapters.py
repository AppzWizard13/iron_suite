from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.exceptions import ImmediateHttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Custom adapter to connect existing users, generate JWT tokens,
        and return additional fields like staff_role, is_staff, and is_superuser.
        """
        print("[ADAPTER] pre_social_login called.")
        email = sociallogin.user.email
        print(f"[ADAPTER] Social user email: {email!r}")

        if not email:
            print("[ADAPTER] No email found in social login.")
            raise ImmediateHttpResponse(
                Response(
                    {"detail": "No email found in social login response."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            )

        try:
            user = User.objects.get(email=email)
            print(f"[ADAPTER] Existing user found: {user}")
            sociallogin.connect(request, user)
            print("[ADAPTER] Social account connected to user.")

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.pk,
                    "email": user.email,
                    "name": user.get_full_name() or user.username,
                    "staff_role": getattr(user, "staff_role", None),
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                },
            }
            print(f"[ADAPTER] JWT tokens generated: {data}")

            # Immediately return JWT in response (REST API context)
            raise ImmediateHttpResponse(Response(data, status=status.HTTP_200_OK))

        except User.DoesNotExist:
            print("[ADAPTER] User not found. Raising error.")
            raise ImmediateHttpResponse(
                Response(
                    {"detail": "User with this email not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            )
