import asyncio

import asyncpg

from src.config import settings


async def main():
    try:
        # Убираем '+asyncpg' из строки, оставляя 'postgresql://...'
        dsn = settings.get_database_url().replace("+asyncpg", "")
        conn = await asyncpg.connect(dsn)
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Connected! PostgreSQL version: {version[:50]}...")
        await conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
