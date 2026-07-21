from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    joinedload,
    mapped_column,
    relationship,
    sessionmaker,
)

DATABASE_URL = "postgresql+psycopg://postgres:12345@localhost:5432/library_db"


class Base(DeclarativeBase):
    pass


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    books: Mapped[list["Book"]] = relationship(back_populates="genre")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    genre_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("genres.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )

    genre: Mapped[Genre] = relationship(back_populates="books")

    def is_available_to_str(self):
        return "Да" if self.is_available else "Нет"


engine = create_engine(DATABASE_URL, echo=False)

get_session_local = sessionmaker(
    bind=engine,
    expire_on_commit=True,
)



def get_all_genres(session: Session) -> list[Genre]:
    query = select(Genre).order_by(Genre.id)
    return list(session.scalars(query).all())


def get_genre_by_id(session: Session, id: int) -> Genre | None:
    return session.get(Genre, id)


def add_genre(session: Session, genre: Genre):
    session.add(genre)
    session.commit()


def update_genre(session: Session, genre: Genre) -> bool:
    find_genre = get_genre_by_id(session, genre.id)
    if find_genre is None:
        return False

    find_genre.name = genre.name
    find_genre.description = genre.description
    session.commit()
    return True


def delete_genre(session: Session, id: int) -> bool:
    find_genre = get_genre_by_id(session, id)
    if find_genre is None:
        return False

    session.delete(find_genre)
    session.commit()
    return True



def get_all_books_with_genres(session: Session) -> list[Book]:
    query = select(Book).options(joinedload(Book.genre)).order_by(Book.id)
    return list(session.scalars(query).all())


def get_book_by_id(session: Session, id: int) -> Book | None:
    return session.get(Book, id)


def add_book(session: Session, book: Book):
    session.add(book)
    session.commit()


def update_book(session: Session, book: Book) -> bool:
    find_book = get_book_by_id(session, book.id)
    if find_book is None:
        return False

    find_book.title = book.title
    find_book.author = book.author
    find_book.publication_year = book.publication_year
    find_book.pages = book.pages
    find_book.is_available = book.is_available
    find_book.genre_id = book.genre_id
    session.commit()
    return True


def delete_book(session: Session, id: int) -> bool:
    find_book = get_book_by_id(session, id)
    if find_book is None:
        return False

    session.delete(find_book)
    session.commit()
    return True



def print_genres_table_header():
    print(f"{'ID':<5}{'NAME':<30}{'DESCRIPTION'}")


def print_one_genre(genre: Genre):
    print(f"{genre.id:<5}{genre.name:<30}{genre.description}")


def print_genres(genres: list[Genre]):
    print("\n--- Жанры ---")
    print_genres_table_header()
    for genre in genres:
        print_one_genre(genre)


def print_books_table_header():
    print(
        f"{'ID':<5}{'TITLE':<30}{'AUTHOR':<25}{'YEAR':<8}{'PAGES':<8}{'AVAILABLE':<10}{'GENRE'}"
    )


def print_one_book(book: Book):
    print(
        f"{book.id:<5}"
        f"{book.title[:28]:<30}"
        f"{book.author[:23]:<25}"
        f"{book.publication_year:<8}"
        f"{book.pages:<8}"
        f"{book.is_available_to_str():<10}"
        f"{book.genre.name}"
    )


def print_books(books: list[Book]):
    print("\n--- Книги ---")
    print_books_table_header()
    for book in books:
        print_one_book(book)


def print_books_with_genres(books: list[Book]):
    print("\n--- Книги с жанрами ---")
    print_books_table_header()
    for book in books:
        print_one_book(book)



def get_available_books(session: Session) -> list[Book]:
    query = (
        select(Book)
        .options(joinedload(Book.genre))
        .where(Book.is_available == True)
        .order_by(Book.id)
    )
    return list(session.scalars(query).all())


def get_books_by_genre(session: Session, genre_id: int) -> list[Book]:
    query = (
        select(Book)
        .options(joinedload(Book.genre))
        .where(Book.genre_id == genre_id)
        .order_by(Book.id)
    )
    return list(session.scalars(query).all())



def main():
    with get_session_local() as session:
        is_run = True

        while is_run:
            try:
                genres = get_all_genres(session)
                print_genres(genres)

                books = get_all_books_with_genres(session)
                print_books_with_genres(books)

                print("\n" + "=" * 100)
                print("Меню:")
                print("  1. Вывести все жанры")
                print("  2. Добавить жанр")
                print("  3. Найти жанр по ID")
                print("  4. Изменить жанр")
                print("  5. Удалить жанр")
                print("-" * 50)
                print("  6. Вывести все книги")
                print("  7. Добавить книгу")
                print("  8. Найти книгу по ID")
                print("  9. Изменить книгу")
                print(" 10. Удалить книгу")
                print("-" * 50)
                print(" 11. Вывести только доступные книги")
                print(" 12. Вывести книги выбранного жанра")
                print("  0. Завершить программу")

                choice = int(input("\nВыберите пункт меню: "))

                
                if choice == 1:
                    genres = get_all_genres(session)
                    print_genres(genres)

                elif choice == 2:
                    name = input("Название жанра: ")
                    description = input("Описание жанра: ")
                    add_genre(session, Genre(name=name, description=description))
                    print("Жанр успешно добавлен!")

                elif choice == 3:
                    id = int(input("Введите ID жанра: "))
                    genre = get_genre_by_id(session, id)
                    if genre is None:
                        print(f"Жанр с ID {id} не найден")
                    else:
                        print_genres_table_header()
                        print_one_genre(genre)

                elif choice == 4:
                    id = int(input("Введите ID жанра: "))
                    name = input("Новое название жанра: ")
                    description = input("Новое описание жанра: ")
                    if update_genre(session, Genre(id=id, name=name, description=description)):
                        print("Жанр успешно обновлен!")
                    else:
                        print(f"Жанр с ID {id} не найден")

                elif choice == 5:
                    id = int(input("Введите ID жанра: "))
                    if delete_genre(session, id):
                        print("Жанр успешно удален!")
                    else:
                        print(f"Жанр с ID {id} не найден")

                
                elif choice == 6:
                    books = get_all_books_with_genres(session)
                    print_books_with_genres(books)

                elif choice == 7:
                    title = input("Название книги: ")
                    author = input("Автор: ")
                    publication_year = int(input("Год публикации: "))
                    pages = int(input("Количество страниц: "))
                    is_available = input("Книга доступна? (да/нет): ").lower() == "да"

                    print("\nДоступные жанры:")
                    genres = get_all_genres(session)
                    print_genres(genres)

                    genre_id = int(input("ID жанра: "))

                    add_book(
                        session,
                        Book(
                            title=title,
                            author=author,
                            publication_year=publication_year,
                            pages=pages,
                            is_available=is_available,
                            genre_id=genre_id,
                        ),
                    )
                    print("Книга успешно добавлена!")

                elif choice == 8:
                    id = int(input("Введите ID книги: "))
                    book = get_book_by_id(session, id)
                    if book is None:
                        print(f"Книга с ID {id} не найдена")
                    else:
                        print_books_table_header()
                        print_one_book(book)

                elif choice == 9:
                    id = int(input("Введите ID книги: "))
                    title = input("Новое название книги: ")
                    author = input("Новый автор: ")
                    publication_year = int(input("Новый год публикации: "))
                    pages = int(input("Новое количество страниц: "))
                    is_available = input("Книга доступна? (да/нет): ").lower() == "да"

                    print("\nДоступные жанры:")
                    genres = get_all_genres(session)
                    print_genres(genres)

                    genre_id = int(input("ID жанра: "))

                    if update_book(
                        session,
                        Book(
                            id=id,
                            title=title,
                            author=author,
                            publication_year=publication_year,
                            pages=pages,
                            is_available=is_available,
                            genre_id=genre_id,
                        ),
                    ):
                        print("Книга успешно обновлена!")
                    else:
                        print(f"Книга с ID {id} не найдена")

                elif choice == 10:
                    id = int(input("Введите ID книги: "))
                    if delete_book(session, id):
                        print("Книга успешно удалена!")
                    else:
                        print(f"Книга с ID {id} не найдена")

                
                elif choice == 11:
                    books = get_available_books(session)
                    if not books:
                        print("Нет доступных книг")
                    else:
                        print_books(books)

                elif choice == 12:
                    print("\nДоступные жанры:")
                    genres = get_all_genres(session)
                    print_genres(genres)

                    genre_id = int(input("Введите ID жанра: "))
                    books = get_books_by_genre(session, genre_id)
                    if not books:
                        print("В этом жанре нет книг")
                    else:
                        print_books(books)

                elif choice == 0:
                    is_run = False
                    print("Программа завершена")

                else:
                    print("Неверный пункт меню!")

                input("\nНажмите Enter для продолжения...")

            except ValueError as e:
                print(f"Ошибка ввода: {e}")
                session.rollback()
                input("\nНажмите Enter для продолжения...")
            except Exception as e:
                print(f"Ошибка: {e}")
                session.rollback()
                input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    main()
