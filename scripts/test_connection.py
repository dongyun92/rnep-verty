#!/usr/bin/env python
"""
Test database connection
"""
import asyncio
import logging
from sqlalchemy import text

from rnep.database.base import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_connection():
    """Test database connection"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info(f"Database connection successful! Result: {result.scalar()}")
            
            # Check PostGIS
            result = await conn.execute(text("SELECT PostGIS_version()"))
            postgis_version = result.scalar()
            logger.info(f"PostGIS version: {postgis_version}")
            
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())