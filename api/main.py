from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import get_settings
from api.routers import matchups, rankings, teams


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="footyIQ API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(teams.router)
    app.include_router(rankings.router)
    app.include_router(matchups.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
