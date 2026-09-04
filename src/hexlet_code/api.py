import json

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from hexlet_code.db import get_session
from hexlet_code.models import Link, LinkCreate, LinkRead, LinkUpdate
from hexlet_code.services import (
    count_links,
    create_link,
    delete_link,
    get_link_by_id,
    get_link_by_short_name,
    get_links,
    update_link,
)
from hexlet_code.settings import get_settings

router = APIRouter()


@router.get("/ping")
def ping() -> str:
    return "pong"


@router.get("/api/links", response_model=list[LinkRead])
def list_links(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
) -> list[LinkRead]:
    total = count_links(session)
    start, end = parse_range(request.query_params.get("range"), total)
    links = get_links(session, start, end)

    response.headers["Content-Range"] = f"links {start}-{end}/{total}"
    return [
        LinkRead.model_validate(link_to_read_model(link, request))
        for link in links
    ]


@router.post(
    "/api/links",
    response_model=LinkRead,
    status_code=status.HTTP_201_CREATED,
)
def create_link_endpoint(
    payload: LinkCreate,
    request: Request,
    session: Session = Depends(get_session),
) -> LinkRead:
    link = create_link(session, payload)
    return LinkRead.model_validate(link_to_read_model(link, request))


@router.get("/api/links/{link_id}", response_model=LinkRead)
def get_link_endpoint(
    link_id: int,
    request: Request,
    session: Session = Depends(get_session),
) -> LinkRead:
    link = get_link_by_id(session, link_id)
    return LinkRead.model_validate(link_to_read_model(link, request))


@router.put("/api/links/{link_id}", response_model=LinkRead)
def update_link_endpoint(
    link_id: int,
    payload: LinkUpdate,
    request: Request,
    session: Session = Depends(get_session),
) -> LinkRead:
    link = get_link_by_id(session, link_id)
    updated_link = update_link(session, link, payload)
    return LinkRead.model_validate(link_to_read_model(updated_link, request))


@router.delete("/api/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link_endpoint(
    link_id: int,
    session: Session = Depends(get_session),
) -> None:
    link = get_link_by_id(session, link_id)
    delete_link(session, link)


@router.get("/r/{short_name}", status_code=status.HTTP_302_FOUND)
def redirect_to_original(
    short_name: str,
    session: Session = Depends(get_session),
) -> RedirectResponse:
    link = get_link_by_short_name(session, short_name)
    return RedirectResponse(
        url=str(link.original_url),
        status_code=status.HTTP_302_FOUND,
    )


def link_to_read_model(link: Link, request: Request) -> dict[str, str | int]:
    settings = get_settings()
    request_base_url = str(request.base_url).rstrip("/")
    base_url = (
        settings.base_url
        if request_base_url == "https://short.test" and settings.base_url
        else request_base_url
    )
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
