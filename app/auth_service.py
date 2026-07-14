import os
import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash


class AuthService:
    """Business logic for authentication and authorization."""

    def __init__(self, user_repository):
        self.user_repository = user_repository
        self.jwt_secret = os.environ.get("JWT_SECRET")

    def register(self, email, password):
        """Hash the password, create the user, raise if email exists."""
        existing = self.user_repository.get_by_email(email)
        if existing:
            raise ValueError("Email already exists")

        password_hash = generate_password_hash(password)
        user = self.user_repository.create(email, password_hash)
        return user

    def login(self, email, password):
        """Verify credentials and return a JWT on success."""
        user = self.user_repository.get_by_email(email)
        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid credentials")

        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token

    def verify_token(self, token):
        """Decode and validate a JWT. Returns the payload or raises."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
