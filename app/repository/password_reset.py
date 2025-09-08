from datetime import datetime, timedelta, timezone
import hashlib
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import PasswordResetToken

from uuid import UUID


class PasswordResetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_password_reset_token(self, user_id: UUID, string_context: str) -> PasswordResetToken:
        """Create and store a password reset token in the database."""
        token_hash = hashlib.sha256(string_context.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        reset_token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        self.session.add(reset_token)
        await self.session.commit()
        await self.session.refresh(reset_token)

        return reset_token

    async def get_valid_reset_token(self, user_id: UUID, token: str) -> Optional[PasswordResetToken]:
        """Retrieve a valid reset token if it exists and is not expired."""
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        stmt = (
            select(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.expires_at > datetime.now(timezone.utc)
            )
        )

        result = await self.session.scalars(stmt)
        return result.first()

    async def delete_reset_token(self, reset_token: PasswordResetToken):
        """Delete a password reset token after it's been used."""
        await self.session.delete(reset_token)
        await self.session.commit()
