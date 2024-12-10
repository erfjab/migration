from sqlalchemy.future import select
from db import Token, GetDB
from ..models import TokenUpsert, TokenData


class TokenManager:
    @staticmethod
    async def upsert(token_upsert: TokenUpsert) -> TokenData:
        async with GetDB() as db:
            result = await db.execute(select(Token).where(Token.id == 1))
            token = result.scalar_one_or_none()

            if token:
                token.token = token_upsert.token
            else:
                token = Token(id=1, token=token_upsert.token)

            db.add(token)
            await db.commit()
            await db.refresh(token)
            return await TokenManager.get()

    @staticmethod
    async def get() -> TokenData:
        async with GetDB() as db:
            result = await db.execute(select(Token).where(Token.id == 1))
            token = result.scalar_one_or_none()
            return TokenData.from_orm(token) if token else None
