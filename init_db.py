import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'showcase_of_projects.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Инициализация базы данных...")

    cur.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            short_description TEXT NOT NULL,
            description TEXT NOT NULL,
            logo_storage_name TEXT,
            status TEXT DEFAULT 'moderation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS project_tags (
            project_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE,
            PRIMARY KEY (project_id, tag_id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS project_departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            department_name TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS project_mentors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            mentor_name TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS project_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            participant_name TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS project_majors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            major_code TEXT NOT NULL,
            major_profile TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS project_partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            partner_name TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS project_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            filename TEXT NOT NULL,
            storage_name TEXT NOT NULL,
            mime_type TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS suggested_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')

    cur.execute("SELECT COUNT(*) FROM tags")
    if cur.fetchone()[0] == 0:
        test_tags = [
            ('Python', 'Языки программирования'),
            ('JavaScript', 'Языки программирования'),
            ('Flask', 'Фреймворки'),
            ('React', 'Фреймворки'),
            ('Машинное обучение', 'Направления'),
            ('Веб-разработка', 'Направления'),
            ('Мобильная разработка', 'Направления'),
            ('Анализ данных', 'Направления')
        ]
        cur.executemany("INSERT OR IGNORE INTO tags (name, category) VALUES (?, ?)", test_tags)
        print("Добавлены тестовые теги")

    conn.commit()
    conn.close()
    print("✅ База данных успешно инициализирована!")


if __name__ == '__main__':
    init_db()