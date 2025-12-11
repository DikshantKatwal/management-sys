from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Read access token from cookies
        access_token = request.COOKIES.get("access")
        if not access_token:
            return None

        # Treat the cookie token as a Bearer token
        raw_token = access_token
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        return (user, validated_token)
