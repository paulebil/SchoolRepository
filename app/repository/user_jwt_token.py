from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from datetime import datetime, timezone

from app.models.user import UserToken
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