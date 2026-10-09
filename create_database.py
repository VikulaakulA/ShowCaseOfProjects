import sqlite3

DB_PATH = 'showcase_of_projects.db'

DDL = '''
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    short_description TEXT, 
    description TEXT,
    logo_storage_name TEXT,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS project_departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    department_name TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    partner_name TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_majors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    major_code TEXT NOT NULL,
    major_profile TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_mentors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    mentor_name TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    participant_name TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    storage_name TEXT NOT NULL,
    mime_type TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT
);

CREATE TABLE IF NOT EXISTS project_tags (
    project_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS suggested_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,        
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_departments_project ON project_departments(project_id);
CREATE INDEX IF NOT EXISTS idx_partners_project ON project_partners(project_id);
CREATE INDEX IF NOT EXISTS idx_majors_project ON project_majors(project_id);
CREATE INDEX IF NOT EXISTS idx_mentors_project ON project_mentors(project_id);
CREATE INDEX IF NOT EXISTS idx_participants_project ON project_participants(project_id);
CREATE INDEX IF NOT EXISTS idx_files_project ON project_files(project_id);
'''

DEFAULT_TAGS = {
 "IT": ["Искусственный интеллект", "Промышленная разработка", "Инновации"],
 "Биология": ["Генетика", "Экология"],
 "Экономика": ["Финансы", "Аналитика"],
 "Медицина": ["Биотех", "Фармацевтика"],
 "Инженерия": ["Робототехника", "Механика"],
 "Другие": ["Образование", "Социальные проекты"]
}

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.executescript(DDL)
        cur.execute("SELECT COUNT(1) as cnt FROM tags")
        row = cur.fetchone()
        if not row or row[0] == 0:
            for cat, tags in DEFAULT_TAGS.items():
                for t in tags:
                    try:
                        cur.execute("INSERT INTO tags (name, category) VALUES (?, ?)", (t, cat))
                    except sqlite3.IntegrityError:
                        pass
        conn.commit()
        print(f"Database ensured at: {DB_PATH}")
    except Exception as e:
        print('Error creating DB:', e)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
