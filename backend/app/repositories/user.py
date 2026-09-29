from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import User


class UserRepository:
    """Database operations for users."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def list_users(self, *, limit: int = 100, offset: int = 0) -> list[User]:
        result = await self.session.execute(
            select(User)
            .order_by(User.id)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        name: str,
        phone_number: str,
        role: str = "trainee",
    ) -> User:
        user = User(
            name=name,
            phone_number=phone_number,
            role=role,
        )

        self.session.add(user)
        await self.session.flush()

        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()