import pytest

from backend.app.db.session import AsyncSessionFactory
from backend.app.repositories import UserRepository


@pytest.mark.asyncio
async def test_create_and_get_user():
    async with AsyncSessionFactory() as session:
        repository = UserRepository(session)

        user = await repository.create(
            name="Test Trainee",
            phone_number="+919999999999",
        )

        await session.commit()

        assert user.id is not None
        assert user.name == "Test Trainee"
        assert user.phone_number == "+919999999999"
        assert user.role == "trainee"

        fetched_user = await repository.get_by_id(user.id)

        assert fetched_user is not None
        assert fetched_user.id == user.id
        assert fetched_user.name == "Test Trainee"

        await session.delete(fetched_user)
        await session.commit()