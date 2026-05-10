from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.db.connection import connect, init_schema
from app.bff.routes.api import router as api_router
from app.config.settings import get_settings
from app.deps import build_deps
from app.domain.models.source import SourceConfig


def seed_sources(deps) -> None:
    deps.source_repo.upsert_source(
        SourceConfig(id="src_fake", name="Fake fixtures", source_type="fake", marketplace="fake"),
        {},
    )
    deps.source_repo.upsert_source(
        SourceConfig(id="src_ebay", name="eBay browse search", source_type="ebay_browse", marketplace="ebay"),
        {"query": "", "limit": 20},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    conn = connect(settings.database_path)
    init_schema(conn)
    deps = build_deps(conn, settings)
    seed_sources(deps)
    app.state.deps = deps
    app.state.settings = settings
    yield
    conn.close()


def create_app() -> FastAPI:
    application = FastAPI(title="Secondhand Feed API", lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    application.include_router(api_router, prefix="/api")
    return application


app = create_app()
