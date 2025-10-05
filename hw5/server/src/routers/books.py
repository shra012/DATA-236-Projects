from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from .. import models, schemas
from ..database import get_db
from ..utils import model_dump

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=schemas.BookOut, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)) -> schemas.BookOut:
    author = db.get(models.Author, book.author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found.")

    db_book = models.Book(**model_dump(book))
    db.add(db_book)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ISBN must be unique.")
    db.refresh(db_book)

    return (
        db.query(models.Book)
        .options(joinedload(models.Book.author))
        .filter(models.Book.id == db_book.id)
        .first()
    )


@router.get("", response_model=schemas.PaginatedBooks)
def list_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> schemas.PaginatedBooks:
    if limit <= 0 or limit > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 1 and 100.")

    total = db.query(func.count(models.Book.id)).scalar() or 0
    books = (
        db.query(models.Book)
        .options(selectinload(models.Book.author))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return schemas.PaginatedBooks(total=total, skip=skip, limit=limit, items=books)


@router.get("/{book_id}", response_model=schemas.BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)) -> schemas.BookOut:
    book = (
        db.query(models.Book)
        .options(joinedload(models.Book.author))
        .filter(models.Book.id == book_id)
        .first()
    )
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")
    return book


@router.put("/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db)) -> schemas.BookOut:
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")

    update_data = {k: v for k, v in model_dump(payload, exclude_unset=True).items() if v is not None}
    if "author_id" in update_data:
        new_author = db.get(models.Author, update_data["author_id"])
        if not new_author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found.")

    for field, value in update_data.items():
        setattr(book, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ISBN must be unique.")

    return (
        db.query(models.Book)
        .options(joinedload(models.Book.author))
        .filter(models.Book.id == book_id)
        .first()
    )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)) -> None:
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")

    db.delete(book)
    db.commit()
