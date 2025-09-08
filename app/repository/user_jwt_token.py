from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from datetime import datetime, timezone

from app.models.user import UserToken, User
from typing import Optional

from uuid import UUID


class UserJwtToken:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_jwt_token(self, jwt_token: UserToken):
        try:
            self.session.add(jwt_token)
            await self.session.commit()
            await self.session.refresh(jwt_token)
            return jwt_token
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_user_token(self,  user_token_id: UUID ,user_id: UUID, access_key: str, ) -> Optional["UserToken"]:
        """
        Fetch a valid user token (with its related user) if it exists and has not expired.
        """
        stmt = (
            select(UserToken)
            .where(
                UserToken.id == user_token_id,
                UserToken.user_id == user_id,
                UserToken.access_key == access_key,
                UserToken.expires_at > datetime.now(timezone.utc),
            )
            .options(joinedload(UserToken.user))
        )

        result = await self.session.scalars(stmt)
        return result.first()

    async def get_valid_user_token_with_user(
            self,
            user_id: UUID,
            access_key: str,
            refresh_key: str
    ) -> tuple[UserToken, User] | None:
        """
        Fetch the first valid user token with matching user_id, access_key,
        and refresh_key that has not expired, along with the associated User object.
        """
        stmt = (
            select(UserToken)
            .options(joinedload(UserToken.user))
            .where(
                UserToken.user_id == user_id,
                UserToken.access_key == access_key,
                UserToken.refresh_key == refresh_key,
                UserToken.expires_at > datetime.now()
            )
        )

        result = await self.session.execute(stmt)
        user_token = result.scalars().first()

        if user_token:
            return user_token, user_token.user
        return None