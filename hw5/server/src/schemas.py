from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class AuthorBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None


class AuthorOut(AuthorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookBase(BaseModel):
    title: str = Field(..., max_length=255)
    isbn: str = Field(..., max_length=13, min_length=10)
    publication_year: int = Field(..., ge=0)
    available_copies: int = Field(default=1, ge=0)
    author_id: int


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    isbn: Optional[str] = Field(default=None, max_length=13, min_length=10)
    publication_year: Optional[int] = Field(default=None, ge=0)
    available_copies: Optional[int] = Field(default=None, ge=0)
    author_id: Optional[int] = None


class BookOut(BookBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: Optional[AuthorOut] = None

    class Config:
        from_attributes = True


class AuthorWithBooks(AuthorOut):
    books: List[BookOut] = Field(default_factory=list)


class PaginatedAuthors(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[AuthorOut]


class PaginatedBooks(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[BookOut]
