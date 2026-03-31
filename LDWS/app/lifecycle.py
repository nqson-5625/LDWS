from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__) # Tạo logger để ghi log

@asynccontextmanager # Decorator
async def lifespan(app: FastAPI):
    # App start
    logger.info("Starting LDWS backend...")
    
    yield # -> App chạy bình thường

    # App stop
    logger.info("Shutting down LDWS backend")