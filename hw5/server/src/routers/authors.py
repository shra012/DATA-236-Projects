"""Author-related API routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas
from ..database import get_db
from ..utils import model_dump

router = APIRouter(prefix="/authors", tags=["authors"])


@router.post("", response_model=schemas.AuthorOut, status_code=status.HTTP_201_CREATED)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)) -> schemas.AuthorOut:
    db_author = models.Author(**model_dump(author))
    db.add(db_author)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")
    db.refresh(db_author)
    return db_author


@router.get("", response_model=schemas.PaginatedAuthors)
def list_authors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> schemas.PaginatedAuthors:
    if limit <= 0 or limit > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 1 and 100.")

    total = db.query(func.count(models.Author.id)).scalar() or 0
    authors = (
        db.query(models.Author)
        .options(selectinload(models.Author.books))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return schemas.PaginatedAuthors(total=total, skip=skip, limit=limit, items=authors)


@router.get("/{author_id}", response_model=schemas.AuthorWithBooks)
def get_author(author_id: int, db: Session = Depends(get_db)) -> schemas.AuthorWithBooks:
    author = (
        db.query(models.Author)
        .options(selectinload(models.Author.books))
        .filter(models.Author.id == author_id)
        .first()
    )
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found.")
    return author


@router.put("/{author_id}", response_model=schemas.AuthorOut)
def update_author(author_id: int, payload: schemas.AuthorUpdate, db: Session = Depends(get_db)) -> schemas.AuthorOut:
    author = db.get(models.Author, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found.")

    update_data = {k: v for k, v in model_dump(payload, exclude_unset=True).items() if v is not None}
    for field, value in update_data.items():
        setattr(author, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")
    db.refresh(author)
    return author


@router.get("/{author_id}/books", response_model=List[schemas.BookOut])
def list_books_by_author(author_id: int, db: Session = Depends(get_db)) -> List[schemas.BookOut]:
    author = db.get(models.Author, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found.")

    books = (
        db.query(models.Book)
        .options(selectinload(models.Book.author))
        .filter(models.Book.author_id == author_id)
        .all()
    )
    return books


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: Session = Depends(get_db)) -> None:
    author = db.get(models.Author, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found.")

    has_books = db.query(models.Book).filter(models.Book.author_id == author_id).first()
    if has_books:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete author with associated books.",
        )

    db.delete(author)
    db.commit()
