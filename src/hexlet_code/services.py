from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from hexlet_code.models import Link, LinkCreate, LinkUpdate


def count_links(session: Session) -> int:
    return session.exec(select(func.count()).select_from(Link)).one()


def get_links(session: Session, start: int, end: int) -> list[Link]:
    statement = select(Link).order_by(Link.id)
    if end <= start:
        return []

    statement = statement.offset(start).limit(end - start)
    return session.exec(statement).all()


def create_link(session: Session, payload: LinkCreate) -> Link:
    link = Link(
        original_url=str(payload.original_url),
        short_name=payload.short_name,
    )
    session.add(link)
    _commit_or_raise_duplicate_short_name(session)
    session.refresh(link)
    return link


def get_link_by_id(session: Session, link_id: int) -> Link:
    link = session.get(Link, link_id)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"link with id {link_id} not found",
        )

    return link


def update_link(session: Session, link: Link, payload: LinkUpdate) -> Link:
    link.sqlmodel_update(
        {
            "original_url": str(payload.original_url),
            "short_name": payload.short_name,
        }
    )
    session.add(link)
    _commit_or_raise_duplicate_short_name(session)
    session.refresh(link)
    return link


def delete_link(session: Session, link: Link) -> None:
    session.delete(link)
    session.commit()


def get_link_by_short_name(session: Session, short_name: str) -> Link:
    statement = select(Link).where(Link.short_name == short_name)
    link = session.exec(statement).first()
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"link with short_name '{short_name}' not found",
        )

    return link


def _commit_or_raise_duplicate_short_name(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="short_name already exists",
        ) from None
