import jwt
import base64
import re
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone


from fastapi.security import OAuth2PasswordBearer

from app.core.settings import Settings
from app.utils.string import unique_string

settings = Settings()

class Security:

    password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    @staticmethod
    def hash_password(password: str) -> str:
        return Security.pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return Security.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def is_password_strong_enough(password: str) -> bool:
        return bool(Security.password_regex.match(password))

    @staticmethod
    def str_encode(plain_str: str) -> str:
        return base64.b64encode(plain_str.encode('utf-8')).decode('utf-8')

    @staticmethod
    def str_decode(encoded_str: str) -> str:
        return base64.b85decode(encoded_str.encode('utf-8')).decode('utf-8')

    @staticmethod
    def generate_token(payload: dict, expiry: timedelta) -> str:
        token_payload = payload.copy()
        token_payload.update({
            "exp": datetime.now(timezone.utc) + expiry,
            "iat": datetime.now(timezone.utc)
        })

        return jwt.encode(token_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def generate_token_pair(self):
        refresh_key = unique_string(100)
        access_key = unique_string(100)
        rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        pass


