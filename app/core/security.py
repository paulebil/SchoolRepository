import logging

import jwt
import base64
import re
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from typing import Optional

from fastapi.security import OAuth2PasswordBearer

from app.core.settings import Settings
from app.utils.string import unique_string

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserToken, User
from app.repository.user_jwt_token import UserJwtToken
from app.database.database import get_session

from app.repository.user import UserRepository
from fastapi  import Depends, HTTPException, status


def get_user_jwt_token_repository(session: AsyncSession = Depends(get_session))-> UserJwtToken:
    user_jwt_token_repository = UserJwtToken(session)
    return user_jwt_token_repository


def get_user_repository(session: AsyncSession = Depends(get_session))-> UserRepository:
    user_repository = UserRepository(session)
    return user_repository

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

    async def generate_token_pair(self, user: User,
                            user_jwt_token_repository: UserJwtToken = Depends(get_user_jwt_token_repository)):

        refresh_key = unique_string(100)
        access_key = unique_string(100)

        rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        user_token = UserToken()
        user_token.user_id = user.id
        user_token.refresh_key = refresh_key
        user_token.access_key = access_key
        user_token.expires_at = datetime.now(timezone.utc) + rt_expires

        await user_jwt_token_repository.create_jwt_token(user_token)

        at_payload = {
            "sub": self.str_encode(str(user.id)),
            "a": access_key,
            "r": self.str_encode(str(user_token.id)),
            "n": self.str_encode(f"{user.first_name},{user.last_name}")
        }

        at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = self.generate_token(at_payload, at_expires)

        rt_payload = {
            "sub": self.str_encode(str(user.id)),
            "t": refresh_key,
            "a": access_key
        }

        refresh_token = self.generate_token(rt_payload, rt_expires)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": at_expires.seconds
        }

    @staticmethod
    def get_token_payload(token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": True})
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})

    async def get_token_user(self, token: str, user_jwt_token_repository: UserJwtToken = Depends(get_user_jwt_token_repository)) -> Optional[User]:
        payload = self.get_token_payload(token)
        if not payload:
            return None

        try:
            user_token_id = self.str_decode(payload.get('r'))
            user_id = self.str_decode(payload.get('sub'))
            access_key = payload.get('a')
            user_token = await user_jwt_token_repository.get_user_token(user_token_id, user_id, access_key)
            return user_token.user if user_token else None
        except Exception as e:
            logging.error(f"Token verification error: {str(e)}")
            return None

    @staticmethod
    async def load_user(email: str, user_repository: UserRepository = Depends(get_user_repository)) -> Optional[User]:

        user = await user_repository.get_user_by_email(email)
        if not user:
            user = None
        return user

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        user = await self.get_token_user(token=token)
        if user is None:
            raise credentials_exception
        return user