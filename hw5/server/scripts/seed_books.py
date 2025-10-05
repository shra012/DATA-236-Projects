"""Seed script to add random authors and books to the database.

Run with the project's python environment. The script reads DB connection from
environment variables (same as the app). It will create authors first (10) and
then create 100 books associated with those authors. It tolerates Faker not
being installed and falls back to simple random generators.
"""

import random
import string
import os
import sys

from sqlalchemy.exc import IntegrityError

# Ensure server/ (parent of src) is on sys.path so we can import the src package
script_dir = os.path.dirname(__file__)
server_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, server_root)

try:
    from faker import Faker
    faker = Faker()
except Exception:
    faker = None

from src.database import SessionLocal, engine
from src import models


def random_isbn():
    # generate a 13-digit numeric string
    return ''.join(random.choices(string.digits, k=13))


def random_title():
    if faker:
        return faker.sentence(nb_words=random.randint(2, 6)).rstrip('.')
    words = [ ''.join(random.choices(string.ascii_lowercase, k=random.randint(3,8))) for _ in range(random.randint(2,6))]
    return ' '.join(w.capitalize() for w in words)


def random_year():
    return random.randint(1900, 2025)


def seed(session, authors_count=10, books_count=100):
    # curated list (same as CLI) of well-known books and their canonical authors
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

    created = 0
    idx = 0
    total = len(BOOKS)

    # existing authors map
    existing = { (a.first_name, a.last_name): a for a in session.query(models.Author).all() }

    # ensure all authors referenced in BOOKS exist in the authors table
    authors_to_ensure = {}
    for _, (first, last), _ in BOOKS:
        key = (first, last)
        if key in existing or key in authors_to_ensure:
            continue
        email = make_email(first, last)
        new_a = models.Author(first_name=first, last_name=last or '', email=email)
        session.add(new_a)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            # someone else inserted; fetch the existing record
            author = session.query(models.Author).filter(models.Author.email == email).first()
        else:
            session.refresh(new_a)
            author = new_a
        existing[key] = author

    import re

    def make_email(first: str, last: str) -> str:
        f = re.sub(r'[^0-9a-z]', '', first.lower())
        l = re.sub(r'[^0-9a-z]', '', last.lower()) if last else ''
        if l:
            return f"{f}.{l}@example.com"
        return f"{f}@example.com"

    while created < books_count:
        title, (first, last), year = BOOKS[idx % total]
        idx += 1

        key = (first, last)
        author = existing.get(key)
        if not author:
            email = make_email(first, last)
            new_a = models.Author(first_name=first, last_name=last or '', email=email)
            session.add(new_a)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                author = session.query(models.Author).filter(models.Author.email == email).first()
            else:
                session.refresh(new_a)
                author = new_a
            existing[key] = author

        isbn = random_isbn()
        copies = random.randint(0, 5)

        b = models.Book(title=title, isbn=isbn, publication_year=year if year>0 else 1900, available_copies=copies, author_id=author.id)
        session.add(b)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            continue
        session.refresh(b)
        created += 1

    print(f"Created {created} books")


if __name__ == '__main__':
    # create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db, authors_count=10, books_count=100)
    finally:
        db.close()
