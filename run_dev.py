#!/usr/bin/env python
"""
Development server runner
"""
import uvicorn
from rnep.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "rnep.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )