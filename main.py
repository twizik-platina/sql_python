import psycopg
from psycopg.rows import dict_row, class_row
from dataclasses import dataclass

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "library_db",
    "user": "postgres",
    "password": "12345",
}


def get_connection():
    return psycopg.connect(**DB_CONFIG)


@dataclass(slots=True)
class Genre:
    name: str
    description: str
    id: int | None = None


@dataclass(slots=True)
class Book:
    title: str
    author: str
    publication_year: int
    pages_count: int
    rating: float
    is_available: bool
    genre_id: int
    id: int | None = None
    genre: Genre | None = None

    def is_available_to_str(self) -> str:
        return "да" if self.is_available else "нет"


def get_all_genres(conn) -> list[Genre]:
    with conn.cursor(row_factory=class_row(Genre)) as cur:
        cur.execute("""
            SELECT id, name, description
            FROM genres
            ORDER BY id ASC
        """)
        return list(cur.fetchall())


def get_genre_by_id(conn, id: int) -> Genre | None:
    with conn.cursor(row_factory=class_row(Genre)) as cur:
        cur.execute(
            "SELECT id, name, description FROM genres WHERE id = %s",
            (id,)
        )
        return cur.fetchone()


def add_new_genre(conn, genre: Genre):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO genres (name, description) VALUES (%s, %s)",
            (genre.name, genre.description)
        )
    conn.commit()


def update_genre_by_id(conn, genre: Genre) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE genres SET name = %s, description = %s WHERE id = %s",
            (genre.name, genre.description, genre.id)
        )
        updated_rows = cur.rowcount
    conn.commit()
    return updated_rows != 0


def delete_genre_by_id(conn, id: int):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM genres WHERE id = %s", (id,))
    conn.commit()


def get_all_books(conn) -> list[Book]:
    with conn.cursor(row_factory=class_row(Book)) as cur:
        cur.execute("""
            SELECT
                id,
                title,
                author,
                publication_year,
                pages_count,
                rating,
                is_available,
                genre_id
            FROM books
            ORDER BY id ASC
        """)
        return list(cur.fetchall())


def get_all_books_with_genres(conn) -> list[Book]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            SELECT
                b.id,
                b.title,
                b.author,
                b.publication_year,
                b.pages_count,
                b.rating,
                b.is_available,
                b.genre_id,
                g.id AS g_id,
                g.name,
                g.description
            FROM books AS b
            JOIN genres AS g ON b.genre_id = g.id
            ORDER BY b.id ASC
        """)
        rows = cur.fetchall()
        books_list = []
        for row in rows:
            genre_obj = Genre(
                id=row['g_id'],
                name=row['name'],
                description=row['description']
            )
            book = Book(
                id=row['id'],
                title=row['title'],
                author=row['author'],
                publication_year=row['publication_year'],
                pages_count=row['pages_count'],
                rating=row['rating'],
                is_available=row['is_available'],
                genre_id=row['genre_id'],
                genre=genre_obj
            )
            books_list.append(book)
        return books_list


def get_book_by_id(conn, id: int) -> Book | None:
    with conn.cursor(row_factory=class_row(Book)) as cur:
        cur.execute("""
            SELECT
                id,
                title,
                author,
                publication_year,
                pages_count,
                rating,
                is_available,
                genre_id
            FROM books
            WHERE id = %s
        """, (id,))
        return cur.fetchone()


def add_new_book(conn, book: Book):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO books
            (title, author, publication_year, pages_count, rating, is_available, genre_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            book.title,
            book.author,
            book.publication_year,
            book.pages_count,
            book.rating,
            book.is_available,
            book.genre_id
        ))
    conn.commit()


def update_book_by_id(conn, book: Book) -> bool:
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE books
            SET
                title = %s,
                author = %s,
                publication_year = %s,
                pages_count = %s,
                rating = %s,
                is_available = %s,
                genre_id = %s
            WHERE id = %s
        """, (
            book.title,
            book.author,
            book.publication_year,
            book.pages_count,
            book.rating,
            book.is_available,
            book.genre_id,
            book.id
        ))
        updated_rows = cur.rowcount
    conn.commit()
    return updated_rows != 0


def delete_book_by_id(conn, id: int):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM books WHERE id = %s", (id,))
    conn.commit()


def print_genres_table_header():
    print("=" * 80)
    print(f"{'ID':<5} {'НАЗВАНИЕ':<25} {'ОПИСАНИЕ':<50}")
    print("-" * 80)


def print_one_genre(genre: Genre):
    print(f"{genre.id:<5} {genre.name:<25} {genre.description:<50}")


def print_genres(genres: list[Genre]):
    print("\n=== ЖАНРЫ (база, бро) ===")
    print_genres_table_header()
    for genre in genres:
        print_one_genre(genre)
    print("=" * 80)


def print_books_table_header():
    print("=" * 130)
    print(f"{'ID':<3} {'НАЗВАНИЕ':<35} {'АВТОР':<25} {'ГОД':<6} {'СТР':<6} {'РЕЙТ':<6} {'ДОСТ':<8} {'ЖАНР ID':<8}")
    print("-" * 130)


def print_one_book(book: Book):
    print(f"{book.id:<3} {book.title:<35} {book.author:<25} {book.publication_year:<6} "
          f"{book.pages_count:<6} {book.rating:<6} {book.is_available_to_str():<8} {book.genre_id:<8}")


def print_books(books: list[Book]):
    print("\n=== КНИГИ (без жанров) ===")
    print_books_table_header()
    for book in books:
        print_one_book(book)
    print("=" * 130)


def print_books_with_genres(books: list[Book]):
    print("\n=== КНИГИ С ЖАНРАМИ (всё по фен-шую) ===")
    print("=" * 150)
    print(f"{'ID':<3} {'НАЗВАНИЕ':<35} {'АВТОР':<25} {'ГОД':<6} {'СТР':<6} {'РЕЙТ':<6} {'ДОСТ':<8} {'ЖАНР':<25}")
    print("-" * 150)
    for book in books:
        genre_name = book.genre.name if book.genre else "Без жанра"
        print(f"{book.id:<3} {book.title:<35} {book.author:<25} {book.publication_year:<6} "
              f"{book.pages_count:<6} {book.rating:<6} {book.is_available_to_str():<8} {genre_name:<25}")
    print("=" * 150)


def input_positive_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            print("Бро, число должно быть положительным! Не тупи)")
        except ValueError:
            print("Ты чё, цифры вводи, а не буквы!") 


def input_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if 0 <= value <= 5:
                return value
            print("Рейтинг от 0 до 5, ясен пень?")
        except ValueError:
            print("Число давай, не выёбывайся!")


def input_bool(prompt: str) -> bool:
    value = input(prompt).strip().lower()
    return value in ('да', 'yes', 'y', 'true', '1', '')


def input_genre() -> Genre:
    print("\n--- Замутим новый жанр ---")
    name = input("Введи название жанра: ").strip()
    description = input("Введи описание жанра: ").strip()
    return Genre(name=name, description=description)


def input_genre_with_id() -> Genre:
    print("\n--- Апдейтим жанр ---")
    id = input_positive_int("Введи ID жанра: ")
    name = input("Введи новое название жанра: ").strip()
    description = input("Введи новое описание жанра: ").strip()
    return Genre(id=id, name=name, description=description)


def input_book() -> Book:
    print("\n--- Запиливаем новую книгу ---")
    title = input("Название книги: ").strip()
    author = input("Автор: ").strip()
    publication_year = input_positive_int("Год публикации: ")
    pages_count = input_positive_int("Количество страниц: ")
    rating = input_float("Рейтинг (0-5): ")
    is_available = input_bool("Есть в наличии? (Enter - нет, любой символ - да): ")
    genre_id = input_positive_int("ID жанра: ")
    return Book(
        title=title,
        author=author,
        publication_year=publication_year,
        pages_count=pages_count,
        rating=rating,
        is_available=is_available,
        genre_id=genre_id
    )


def input_book_with_id() -> Book:
    print("\n--- Апдейтим книгу ---")
    id = input_positive_int("Введи ID книги: ")
    title = input("Новое название книги: ").strip()
    author = input("Новый автор: ").strip()
    publication_year = input_positive_int("Год публикации: ")
    pages_count = input_positive_int("Количество страниц: ")
    rating = input_float("Рейтинг (0-5): ")
    is_available = input_bool("Есть в наличии? (Enter - нет, любой символ - да): ")
    genre_id = input_positive_int("ID жанра: ")
    return Book(
        id=id,
        title=title,
        author=author,
        publication_year=publication_year,
        pages_count=pages_count,
        rating=rating,
        is_available=is_available,
        genre_id=genre_id
    )


def main():
    with get_connection() as conn:
        is_run = True
        while is_run:
            try:
                books_with_genres = get_all_books_with_genres(conn)
                print_books_with_genres(books_with_genres)
                print("\n" + "=" * 50 + "\n")
                genres = get_all_genres(conn)
                print_genres(genres)
                print("\n" + "=" * 100 + "\n")
                print("МЕНЮ (выбирай с умом):")
                print("1. Найти жанр по id (ну ты понял)")
                print("2. Добавить жанр (замутить новый)")
                print("3. Удалить жанр (кинуть в корзину)")
                print("4. Обновить жанр (апдейтнуть)")
                print("5. Найти книгу по id (чекай)")
                print("6. Добавить книгу (запилить новую)")
                print("7. Удалить книгу (в топку)")
                print("8. Обновить книгу (рефакторим)")
                print("9. Выход (адьос мабой)")
                
                menu_number = int(input("\nНу чё выберешь? "))
                
                if menu_number == 1:
                    genre_id = input_positive_int("Введи ID жанра, бро: ")
                    genre = get_genre_by_id(conn, genre_id)
                    if genre:
                        print("\n=== ВОТ ОН, ЖАНРЮГА ===")
                        print_genres_table_header()
                        print_one_genre(genre)
                        print("=" * 80)
                    else:
                        print(f"\nЖанр с ID {genre_id} не найден! Ты чё, прикалываешься?")
                        
                elif menu_number == 2:
                    try:
                        genre = input_genre()
                        add_new_genre(conn, genre)
                        print("\nЖанр замутили! Красавчик!")
                    except psycopg.errors.UniqueViolation:
                        print("\nТакой жанр уже есть! Не канает!")
                        conn.rollback()
                    except Exception as e:
                        print(f"\nОшибочка вышла: {e}")
                        conn.rollback()
                        
                elif menu_number == 3:
                    genre_id = input_positive_int("Какой жанр в топку? Введи ID: ")
                    try:
                        delete_genre_by_id(conn, genre_id)
                        print(f"\nЖанр с ID {genre_id} улетел в небытие!")
                    except psycopg.errors.ForeignKeyViolation:
                        print(f"\nНе, так не пойдёт! На этом жанре книги висят. Сначала книги удали!")
                        conn.rollback()
                    except Exception as e:
                        print(f"\nОшибочка: {e}")
                        conn.rollback()
                        
                elif menu_number == 4:
                    try:
                        genre = input_genre_with_id()
                        if update_genre_by_id(conn, genre):
                            print(f"\nЖанр с ID {genre.id} обновили! Зачот!")
                        else:
                            print(f"\nЖанр с ID {genre.id} не найден. Ты чё, с дуба рухнул?")
                    except psycopg.errors.UniqueViolation:
                        print("\nТакой жанр уже есть! Не прокатит!")
                        conn.rollback()
                    except Exception as e:
                        print(f"\nОшибочка: {e}")
                        conn.rollback()
                        
                elif menu_number == 5:
                    book_id = input_positive_int("Введи ID книги, братан: ")
                    book = get_book_by_id(conn, book_id)
                    if book:
                        print("\n=== ВОТ ЭТА КНИГА (шедевр!) ===")
                        print_books_table_header()
                        print_one_book(book)
                        print("=" * 130)
                    else:
                        print(f"\nКнига с ID {book_id} не найдена! Может, её украли?")
                        
                elif menu_number == 6:
                    try:
                        book = input_book()
                        add_new_book(conn, book)
                        print("\nКнигу запилили! Жиза!")
                    except psycopg.errors.ForeignKeyViolation:
                        print("\nТакого жанра нет в природе! Введи нормальный ID!")
                        conn.rollback()
                    except Exception as e:
                        print(f"\nОшибочка: {e}")
                        conn.rollback()
                        
                elif menu_number == 7:
                    book_id = input_positive_int("Какую книгу в топку? Введи ID: ")
                    try:
                        delete_book_by_id(conn, book_id)
                        print(f"\nКнига с ID {book_id} отправилась в Вальгаллу!")
                    except Exception as e:
                        print(f"\nОшибочка: {e}")
                        conn.rollback()
                        
                elif menu_number == 8:
                    try:
                        book = input_book_with_id()
                        if update_book_by_id(conn, book):
                            print(f"\nКнига с ID {book.id} обновлена! Теперь она имба!")
                        else:
                            print(f"\nКнига с ID {book.id} не найдена! Может, её уже кто-то спёр?")
                    except psycopg.errors.ForeignKeyViolation:
                        print("\nТакого жанра нет! Введи правильный ID!")
                        conn.rollback()
                    except Exception as e:
                        print(f"\nОшибочка: {e}")
                        conn.rollback()
                        
                elif menu_number == 9:
                    print("\nАдьос мабой! Пока-пока, бро!")
                    is_run = False
                    
                else:
                    print("\nТы чё, с луны упал? Введи число от 1 до 9!")
                    
                input("\nНажми Enter, чтобы продолжить (ну давай, не тяни)...")
                
            except ValueError as e:
                print(f"\nОшибка ввода! Ты чё, тупишь? {e}")
                input("\nНажми Enter...")
            except Exception as e:
                print(f"\nВсё сломалось! Краш! {e}")
                is_run = False


if __name__ == "__main__":
    main()
