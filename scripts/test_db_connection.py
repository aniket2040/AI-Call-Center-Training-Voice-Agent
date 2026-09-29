import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.app.config import settings


async def main() -> None:
    engine = create_async_engine(settings.database_url)

    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print("Database connection successful:", result.scalar())

    except Exception as exc:
        print("Database connection failed:")
        print(type(exc).__name__)
        print(exc)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())