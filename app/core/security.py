import jwt
import base64
import re
from passlib.context import CryptContext


from fastapi.security import OAuth2PasswordBearer

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

