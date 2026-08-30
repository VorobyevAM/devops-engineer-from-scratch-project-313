import json
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from devops_engineer_from_scratch_project_313.db import (
    create_db_and_tables,
    get_session,
)
from devops_engineer_from_scratch_project_313.models import (
    Link,
    LinkCreate,
    LinkRead,
    LinkUpdate,
)
from devops_engineer_from_scratch_project_313.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.0,
        )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        create_db_and_tables(settings.database_url)
        yield

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Range"],
        expose_headers=["Content-Range"],
    )

    @app.get("/ping")
    def ping() -> str:
        return "pong"

    @app.get("/api/links", response_model=list[LinkRead])
    def list_links(
        request: Request,
        response: Response,
        session: Session = Depends(get_session),
    ) -> list[LinkRead]:
        total = session.exec(select(func.count()).select_from(Link)).one()
        start, end = parse_range(request.query_params.get("range"), total)

        statement = select(Link).order_by(Link.id)
        if end > start:
            statement = statement.offset(start).limit(end - start)
            links = session.exec(statement).all()
        else:
            links = []

        response.headers["Content-Range"] = f"links {start}-{end}/{total}"
        return [
            LinkRead.model_validate(link_to_read_model(link, request))
            for link in links
        ]

    @app.post(
        "/api/links",
        response_model=LinkRead,
        status_code=status.HTTP_201_CREATED,
    )
    def create_link(
        payload: LinkCreate,
        request: Request,
        session: Session = Depends(get_session),
    ) -> LinkRead:
        link = Link(
            original_url=str(payload.original_url),
            short_name=payload.short_name,
        )
        session.add(link)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="short_name already exists",
            ) from None

        session.refresh(link)
        return LinkRead.model_validate(link_to_read_model(link, request))

    @app.get("/api/links/{link_id}", response_model=LinkRead)
    def get_link(
        link_id: int,
        request: Request,
        session: Session = Depends(get_session),
    ) -> LinkRead:
        link = get_link_or_404(session, link_id)
        return LinkRead.model_validate(link_to_read_model(link, request))

    @app.put("/api/links/{link_id}", response_model=LinkRead)
    def update_link(
        link_id: int,
        payload: LinkUpdate,
        request: Request,
        session: Session = Depends(get_session),
    ) -> LinkRead:
        link = get_link_or_404(session, link_id)
        link.sqlmodel_update(
            {
                "original_url": str(payload.original_url),
                "short_name": payload.short_name,
            }
        )
        session.add(link)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="short_name already exists",
            ) from None

        session.refresh(link)
        return LinkRead.model_validate(link_to_read_model(link, request))

    @app.delete("/api/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_link(
        link_id: int,
        session: Session = Depends(get_session),
    ) -> None:
        link = get_link_or_404(session, link_id)
        session.delete(link)
        session.commit()

    @app.get("/r/{short_name}", status_code=status.HTTP_302_FOUND)
    def redirect_to_original(
        short_name: str,
        session: Session = Depends(get_session),
    ) -> RedirectResponse:
        statement = select(Link).where(Link.short_name == short_name)
        link = session.exec(statement).first()
        if link is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"link with short_name '{short_name}' not found",
            )

        return RedirectResponse(
            url=str(link.original_url),
            status_code=status.HTTP_302_FOUND,
        )

    return app


def get_link_or_404(session: Session, link_id: int) -> Link:
    link = session.get(Link, link_id)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"link with id {link_id} not found",
        )

    return link


def link_to_read_model(link: Link, request: Request) -> dict[str, str | int]:
    settings = get_settings()
    base_url = settings.base_url or str(request.base_url).rstrip("/")
    return {
        "id": link.id,
        "original_url": str(link.original_url),
        "short_name": link.short_name,
        "short_url": f"{base_url}/r/{link.short_name}",
    }


def parse_range(raw_range: str | None, total: int) -> tuple[int, int]:
    if raw_range is None:
        return 0, total

    try:
        start, end = json.loads(raw_range)
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="invalid range parameter",
        ) from error

    if not isinstance(start, int) or not isinstance(end, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="invalid range parameter",
        )

    if start < 0 or end < start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="invalid range parameter",
        )

    return start, end
