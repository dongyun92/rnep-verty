#!/usr/bin/env python
"""
Initialize database with tables and sample data
"""
import asyncio
import json
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine
from alembic.config import Config
from alembic import command

from rnep.config.settings import settings
from rnep.database.base import Base, engine, async_session_maker
from rnep.database.models import Aircraft

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    """Create all tables"""
    async with engine.begin() as conn:
        # Create PostGIS extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def load_aircraft_data():
    """Load sample aircraft data"""
    aircraft_dir = Path("data/aircraft")
    
    async with async_session_maker() as session:
        # Check if data already exists
        result = await session.execute("SELECT COUNT(*) FROM aircraft")
        count = result.scalar()
        
        if count > 0:
            logger.info(f"Aircraft data already exists ({count} records)")
            return
        
        # Load aircraft data files
        for json_file in aircraft_dir.glob("*.json"):
            with open(json_file, "r") as f:
                data = json.load(f)
                
            aircraft = Aircraft(**data)
            session.add(aircraft)
            logger.info(f"Loaded aircraft: {aircraft.name}")
        
        await session.commit()
        logger.info("Aircraft data loaded successfully")


def run_migrations():
    """Run Alembic migrations"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Migrations completed successfully")


async def init_db():
    """Initialize database"""
    try:
        # Option 1: Use Alembic migrations (recommended)
        logger.info("Running database migrations...")
        run_migrations()
        
        # Option 2: Create tables directly (for development)
        # logger.info("Creating database tables...")
        # await create_tables()
        
        # Load sample data
        logger.info("Loading sample data...")
        await load_aircraft_data()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())