from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.signup_token import SignupToken

class SignupTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_signup_token(self, signup_token: SignupToken):
        try:
            self.session.add(signup_token)
            await self.session.commit()
            await self.session.refresh(signup_token)
            return signup_token
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_signup_token_by_token(self,token: str ):
        stmt = select(SignupToken).where(SignupToken.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
