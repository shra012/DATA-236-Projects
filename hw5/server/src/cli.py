from typing import List
import re

import typer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Author, Book

app = typer.Typer(help="Utility commands for managing the library database")

DEFAULT_AUTHORS = [
    {"first_name": "J.K.", "last_name": "Rowling", "email": "jk.rowling@example.com"},
    {"first_name": "George", "last_name": "Orwell", "email": "george.orwell@example.com"},
    {"first_name": "Agatha", "last_name": "Christie", "email": "agatha.christie@example.com"},
    {"first_name": "Haruki", "last_name": "Murakami", "email": "haruki.murakami@example.com"},
    {"first_name": "Chinua", "last_name": "Achebe", "email": "chinua.achebe@example.com"},
    {"first_name": "Shravankumar", "last_name": "Nagarajan", "email": "shravan_fisher@live.com"},
]

BOOKS = [
    ("1984", ("George", "Orwell"), 1949),
    ("Animal Farm", ("George", "Orwell"), 1945),
    ("Pride and Prejudice", ("Jane", "Austen"), 1813),
    ("The Great Gatsby", ("F. Scott", "Fitzgerald"), 1925),
    ("To Kill a Mockingbird", ("Harper", "Lee"), 1960),
    ("One Hundred Years of Solitude", ("Gabriel Garcia", "Marquez"), 1967),
    ("The Hobbit", ("J.R.R.", "Tolkien"), 1937),
    ("The Catcher in the Rye", ("J.D.", "Salinger"), 1951),
    ("Moby-Dick", ("Herman", "Melville"), 1851),
    ("War and Peace", ("Leo", "Tolstoy"), 1869),
    ("Crime and Punishment", ("Fyodor", "Dostoevsky"), 1866),
    ("The Old Man and the Sea", ("Ernest", "Hemingway"), 1952),
    ("The Stranger", ("Albert", "Camus"), 1942),
    ("A Tale of Two Cities", ("Charles", "Dickens"), 1859),
    ("Brave New World", ("Aldous", "Huxley"), 1932),
    ("The Sound and the Fury", ("William", "Faulkner"), 1929),
    ("Wuthering Heights", ("Emily", "Brontë"), 1847),
    ("The Brothers Karamazov", ("Fyodor", "Dostoevsky"), 1880),
    ("Great Expectations", ("Charles", "Dickens"), 1861),
    ("The Odyssey", ("Homer", ""), -800),
]


def _make_email(first: str, last: str) -> str:
    first_clean = re.sub(r"[^0-9a-z]", "", first.lower())
    last_clean = re.sub(r"[^0-9a-z]", "", last.lower()) if last else ""
    if last_clean:
        return f"{first_clean}.{last_clean}@example.com"
    return f"{first_clean}@example.com"


def _authors_from_books() -> list[dict]:
    seen = set()
    out = []
    for _, (first, last), _ in BOOKS:
        key = (first, last)
        if key in seen:
            continue
        seen.add(key)
        out.append({"first_name": first, "last_name": last or "", "email": _make_email(first, last)})
    return out


def _upsert_authors(db: Session, authors: List[dict]) -> tuple[int, int]:
    inserted = 0
    skipped = 0
    for author in authors:
        exists = (
            db.query(Author)
            .filter(Author.email == author["email"])
            .first()
        )
        if exists:
            skipped += 1
            continue
        db.add(Author(**author))
        inserted += 1
    return inserted, skipped


def seed_books(db: Session, authors_pool: List[Author], count: int = 100) -> int:
    import random
    import string

    created = 0
    idx = 0
    total = len(BOOKS)
    author_map = {(author.first_name, author.last_name): author for author in authors_pool}

    while created < count:
        title, (first, last), year = BOOKS[idx % total]
        idx += 1

        key = (first, last)
        author = author_map.get(key)
        if not author:
            email = _make_email(first, last)
            new_author = Author(first_name=first, last_name=last or "", email=email)
            db.add(new_author)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                author = db.query(Author).filter(Author.email == email).first()
            else:
                db.refresh(new_author)
                author = new_author
            author_map[key] = author

        isbn = "".join(random.choices(string.digits, k=13))
        copies = random.randint(0, 5)

        book = Book(
            title=title,
            isbn=isbn,
            publication_year=year if year > 0 else 1900,
            available_copies=copies,
            author_id=author.id,
        )
        db.add(book)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(book)
        created += 1

    return created


@app.command("seed-books")
def cli_seed_books(count: int = 100) -> None:
    db = SessionLocal()
    try:
        authors = db.query(Author).all()
        if not authors:
            typer.echo("No authors found. Inserting authors referenced by BOOKS list...")
            payload = _authors_from_books()
            inserted, skipped = _upsert_authors(db, payload)
            db.commit()
            typer.echo(f"Inserted {inserted} author(s); skipped {skipped} existing author(s).")
            authors = db.query(Author).all()

        created = seed_books(db, authors, count=count)
    finally:
        db.close()

    typer.echo(f"Created {created} books.")


@app.command("remove-books")
def cli_remove_books(all: bool = typer.Option(False, help="Remove all books.")) -> None:
    db = SessionLocal()
    try:
        if all:
            deleted = db.query(Book).delete()
            db.commit()
            typer.echo(f"Deleted {deleted} books.")
        else:
            typer.echo("No action taken. Use --all to delete all books.")
    finally:
        db.close()


@app.command("remove-authors")
def cli_remove_authors(all: bool = typer.Option(False, help="Remove all authors.")) -> None:
    db = SessionLocal()
    try:
        if all:
            deleted = db.query(Author).delete()
            db.commit()
            typer.echo(f"Deleted {deleted} authors.")
        else:
            typer.echo("No action taken. Use --all to delete all authors.")
    finally:
        db.close()
