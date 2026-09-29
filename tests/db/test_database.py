from sqlalchemy import text

from backend.app.db.session import AsyncSessionFactory, engine


async def test_database_connection():
    async with AsyncSessionFactory() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


async def test_database_engine():
    assert engine.url.drivername == "postgresql+asyncpg"