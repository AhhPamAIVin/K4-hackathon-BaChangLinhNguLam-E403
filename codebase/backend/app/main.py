from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router
from backend.app.core.config import Settings
from backend.app.dependencies import (
    get_summary_knowledge_base,
    get_transcript_knowledge_base,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_transcript_knowledge_base()
    get_summary_knowledge_base()
    yield


settings = Settings.from_env()
app = FastAPI(
    title="VLearn AI Backend",
    version="0.1.0",
    description="Backend cho agent hỏi đáp trực tiếp và agent học tập.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
