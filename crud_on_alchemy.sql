-- Удаляем существующие таблицы
DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS genres CASCADE;

-- Создаем таблицу жанров
CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500) NOT NULL
);

-- Создаем таблицу книг с правильной структурой
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publication_year INTEGER NOT NULL,
    pages INTEGER NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    genre_id INTEGER NOT NULL,
    CONSTRAINT fk_books_genre_id FOREIGN KEY (genre_id) 
        REFERENCES genres(id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Добавляем тестовые данные
INSERT INTO genres (name, description) VALUES
    ('Фэнтези', 'Книги с магией, вымышленными мирами и приключениями'),
    ('Научная фантастика', 'Книги про технологии, космос, будущее и научные идеи'),
    ('Детектив', 'Книги с расследованиями, загадками и поиском преступника'),
    ('Программирование', 'Книги про разработку, алгоритмы и компьютерные технологии'),
    ('Классика', 'Известные произведения, которые считаются важными в литературе');

INSERT INTO books (title, author, publication_year, pages, is_available, genre_id) VALUES
    ('Властелин колец', 'Дж. Р. Р. Толкин', 1954, 1178, TRUE, 1),
    ('Гарри Поттер и философский камень', 'Дж. К. Роулинг', 1997, 332, TRUE, 1),
    ('1984', 'Джордж Оруэлл', 1949, 328, TRUE, 5),
    ('Преступление и наказание', 'Фёдор Достоевский', 1866, 671, FALSE, 5),
    ('Игра престолов', 'Джордж Мартин', 1996, 694, TRUE, 1),
    ('Автостопом по галактике', 'Дуглас Адамс', 1979, 224, TRUE, 2),
    ('Солярис', 'Станислав Лем', 1961, 204, FALSE, 2);
