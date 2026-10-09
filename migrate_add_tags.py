import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "showcase_of_projects.db")

conn = sqlite3.connect(DB_PATH)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS project_tags (
    project_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(project_id, tag_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS suggested_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,        
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
""")

cur.execute("SELECT COUNT(*) FROM tags")
count = cur.fetchone()[0]

if count == 0:
    tags = {
        "IT": [
            "Искусственный интеллект",
            "Промышленная разработка",
            "Инновации",
            "Веб-разработка",
            "Анализ данных"
        ],
        "Биология": [
            "Генетика",
            "Экология",
            "Биотехнологии"
        ],
        "Экономика": [
            "Финансы",
            "Бизнес-аналитика",
            "Экономическое моделирование"
        ],
        "Медицина": [
            "Медицинские технологии",
            "Фармакология",
            "Биомедицина"
        ],
        "Инженерия": [
            "Робототехника",
            "Мехатроника",
            "Инженерное проектирование"
        ],
        "Другие": [
            "Образование",
            "Социальные проекты",
            "Экология общества"
        ]
    }

    for category, items in tags.items():
        for tag in items:
            cur.execute(
                "INSERT INTO tags (name, category) VALUES (?, ?)",
                (tag, category)
            )

conn.commit()
conn.close()

