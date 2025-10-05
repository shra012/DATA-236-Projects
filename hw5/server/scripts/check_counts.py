from src.database import SessionLocal
from src.models import Book, Author

def main():
    s = SessionLocal()
    try:
        print('authors:', s.query(Author).count())
        print('books:', s.query(Book).count())
        sample = s.query(Book).limit(5).all()
        for b in sample:
            print(b.title, b.isbn, b.publication_year)
    finally:
        s.close()

if __name__ == '__main__':
    main()
