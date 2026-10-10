import os
import uuid
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, abort, session, send_from_directory, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(BASE_DIR, 'data'))
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, 'showcase_of_projects.db')

UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-secret")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "qwerty")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "12345")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.create_function("LOWER", 1, lambda s: s.lower() if s else s)
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn


def is_admin_logged_in():
    return session.get('admin_logged_in', False)

@app.template_filter('format_date')
def format_date(value):
    if not value: return "Недавно"
    try:
        date_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return date_obj.strftime('%d.%m.%Y')
    except:
        return value

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in():
        return redirect(url_for('admin'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = "Неверное имя пользователя или пароль"
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))


def fetch_all_tags_grouped(conn):
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, category FROM tags")
        rows = cur.fetchall()
    except Exception:
        return {}
    grouped = {}
    for r in rows:
        cat = r['category'] or 'Другие'
        grouped.setdefault(cat, []).append(dict(id=r['id'], name=r['name']))
    return grouped


@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    search_query = request.args.get('search', '').strip()
    selected_tag_ids = request.args.getlist('tags')

    query = """
        SELECT p.id, p.title, p.short_description, p.description, p.logo_storage_name,
                p.created_at,  -- Добавьте эту строку
                GROUP_CONCAT(t.id, ',') as tag_ids,
                GROUP_CONCAT(t.name, ',') as tag_names
        FROM projects p
        LEFT JOIN project_tags ptg ON p.id = ptg.project_id
        LEFT JOIN tags t ON ptg.tag_id = t.id
        WHERE p.status='posted'
    """

    params = []

    if search_query:
        query += " AND LOWER(p.title) LIKE LOWER(?)"
        params.append(f'%{search_query}%')

    if selected_tag_ids:
        placeholders = ','.join(['?'] * len(selected_tag_ids))
        query += f"""
            AND p.id IN (
                SELECT project_id 
                FROM project_tags 
                WHERE tag_id IN ({placeholders})
            )
        """
        params.extend(selected_tag_ids)

    query += " GROUP BY p.id ORDER BY p.created_at DESC"

    cur.execute(query, params)
    projects = cur.fetchall()

    tags_grouped = fetch_all_tags_grouped(conn)
    conn.close()

    projects_list = []
    for p in projects:
        p_dict = dict(p)
        if p_dict.get('tag_ids') and p_dict.get('tag_names'):
            t_ids = p_dict['tag_ids'].split(',')
            t_names = p_dict['tag_names'].split(',')
            p_dict['tags'] = []
            for i in range(min(len(t_ids), len(t_names))):
                if t_ids[i] and t_names[i]:
                    p_dict['tags'].append({
                        'id': int(t_ids[i]),
                        'name': t_names[i].strip()
                    })
        else:
            p_dict['tags'] = []

        p_dict.pop('tag_ids', None)
        p_dict.pop('tag_names', None)
        projects_list.append(p_dict)

    return render_template("index.html",
                           projects=projects_list,
                           tags_grouped=tags_grouped,
                           selected_tags=selected_tag_ids,
                           is_admin=is_admin_logged_in())


@app.route('/submit_project', methods=['GET'])
def submit_project_form():
    conn = get_db_connection()
    tags_grouped = fetch_all_tags_grouped(conn)
    conn.close()

    return render_template('form.html', tags_grouped=tags_grouped, is_student=True)


@app.route('/submit_project', methods=['POST'])
def submit_project():
    try:
        title = request.form.get('title', '').strip()
        short_description = request.form.get('short_description', '').strip()
        description = request.form.get('description', '').strip()
        custom_tag = request.form.get('custom_tag', '').strip()

        departments = request.form.getlist('departments[]')
        mentors = request.form.getlist('mentors[]')
        participants = request.form.getlist('participants[]')
        major_codes = request.form.getlist('major_codes[]')
        major_profiles = request.form.getlist('major_profiles[]')
        partners = request.form.getlist('partners[]')
        selected_tags = request.form.getlist('tags')

        errors = []
        if not title:
            errors.append('Название проекта обязательно')
        if not short_description:
            errors.append('Краткое описание проекта обязательно')
        if not description:
            errors.append('Описание проекта обязательно')
        if not departments or not all(dept.strip() for dept in departments):
            errors.append('Добавьте хотя бы один департамент/кафедру')
        if not mentors or not all(mentor.strip() for mentor in mentors):
            errors.append('Добавьте хотя бы одного наставника')
        if not major_codes or not all(code.strip() for code in major_codes):
            errors.append('Добавьте хотя бы одно направление обучения')
        if not major_profiles or not all(profile.strip() for profile in major_profiles):
            errors.append('Добавьте описание для всех направлений')
        if not partners or not all(partner.strip() for partner in partners):
            errors.append('Добавьте хотя бы одного заказчика/партнера')
        if not participants or not all(p.strip() for p in participants):
            errors.append('Добавьте хотя бы одного участника проекта')

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('submit_project_form'))

        conn = get_db_connection()
        saved_paths = []

        try:
            cur = conn.cursor()

            logo_file = request.files.get('logo')
            logo_storage_name = None

            if logo_file and logo_file.filename:
                if logo_file.mimetype.startswith('image/'):
                    orig_raw = logo_file.filename
                    orig = secure_filename(orig_raw)
                    if not orig:
                        _, ext = os.path.splitext(orig_raw)
                        orig = f"logo{ext or ''}"
                    unique = f"logo_{uuid.uuid4().hex}_{orig}"
                    path = os.path.join(UPLOAD_FOLDER, unique)
                    logo_file.save(path)
                    logo_storage_name = unique
                    saved_paths.append(path)
                else:
                    flash('Логотип должен быть изображением', 'warning')

            cur.execute("""
                INSERT INTO projects (title, short_description, description, 
                                     logo_storage_name, status) 
                VALUES (?, ?, ?, ?, 'moderation')
            """, (title, short_description, description, logo_storage_name))
            project_id = cur.lastrowid

            for dept in departments:
                if dept.strip():
                    cur.execute("INSERT INTO project_departments (project_id, department_name) VALUES (?, ?)",
                                (project_id, dept.strip()))

            for mentor in mentors:
                if mentor.strip():
                    cur.execute("INSERT INTO project_mentors (project_id, mentor_name) VALUES (?, ?)",
                                (project_id, mentor.strip()))

            for participant in participants:
                if participant.strip():
                    cur.execute("INSERT INTO project_participants (project_id, participant_name) VALUES (?, ?)",
                                (project_id, participant.strip()))

            for code, profile in zip(major_codes, major_profiles):
                if code.strip() and profile.strip():
                    cur.execute("INSERT INTO project_majors (project_id, major_code, major_profile) VALUES (?, ?, ?)",
                                (project_id, code.strip(), profile.strip()))

            for partner in partners:
                if partner.strip():
                    cur.execute("INSERT INTO project_partners (project_id, partner_name) VALUES (?, ?)",
                                (project_id, partner.strip()))

            project_files = request.files.getlist('project_files[]')
            for f in project_files:
                if f and getattr(f, 'filename', None) and f.filename.strip():
                    orig_raw = f.filename
                    orig = secure_filename(orig_raw)
                    if not orig:
                        _, ext = os.path.splitext(orig_raw)
                        orig = f"file{ext or ''}"
                    unique = f"{uuid.uuid4().hex}_{orig}"
                    path = os.path.join(UPLOAD_FOLDER, unique)
                    f.save(path)
                    saved_paths.append(path)
                    cur.execute("""
                        INSERT INTO project_files (project_id, filename, storage_name, mime_type) 
                        VALUES (?, ?, ?, ?)
                    """, (project_id, orig, unique, f.mimetype))

            for tag_id in selected_tags:
                try:
                    tag_id_int = int(tag_id)
                    cur.execute("INSERT INTO project_tags (project_id, tag_id) VALUES (?,?)",
                                (project_id, tag_id_int))
                except Exception as e:
                    print(f"Ошибка при добавлении тега {tag_id}: {e}")

            if custom_tag.strip():
                try:
                    cur.execute(
                        "INSERT INTO suggested_tags (project_id, name, status) VALUES (?, ?, 'pending')",
                        (project_id, custom_tag.strip())
                    )
                except Exception as e:
                    print(f"Ошибка при добавлении предложенного тега: {e}")

            conn.commit()
            flash(f'Проект "{title}" успешно отправлен на модерацию!', 'success')

        except Exception as e:
            conn.rollback()
            print(f"Ошибка БД: {e}")
            import traceback
            traceback.print_exc()

            for p in saved_paths:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except:
                    pass

            flash(f'Ошибка при отправке проекта: {str(e)}', 'error')
            return redirect(url_for('submit_project_form'))
        finally:
            conn.close()

    except Exception as e:
        print(f"Общая ошибка: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Ошибка при обработке формы: {str(e)}', 'error')
        return redirect(url_for('submit_project_form'))

    return redirect(url_for('index'))


@app.route('/admin/forms', methods=['GET'])
def admin_forms():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    tags_grouped = fetch_all_tags_grouped(conn)
    conn.close()

    return render_template('form.html', tags_grouped=tags_grouped, is_student=False)


@app.route('/admin/create', methods=['POST'])
def admin_create():
    if not is_admin_logged_in():
        flash('Требуется авторизация', 'error')
        return redirect(url_for('admin_login'))

    try:
        title = request.form.get('title', '').strip()
        short_description = request.form.get('short_description', '').strip()
        description = request.form.get('description', '').strip()
        custom_tag = request.form.get('custom_tag', '').strip()

        departments = request.form.getlist('departments[]')
        mentors = request.form.getlist('mentors[]')
        participants = request.form.getlist('participants[]')
        major_codes = request.form.getlist('major_codes[]')
        major_profiles = request.form.getlist('major_profiles[]')
        partners = request.form.getlist('partners[]')
        selected_tags = request.form.getlist('tags')

        errors = []
        if not title:
            errors.append('Название проекта обязательно')
        if not short_description:
            errors.append('Краткое описание проекта обязательно')
        if not description:
            errors.append('Описание проекта обязательно')
        if not departments or not all(dept.strip() for dept in departments):
            errors.append('Добавьте хотя бы один департамент/кафедру')
        if not mentors or not all(mentor.strip() for mentor in mentors):
            errors.append('Добавьте хотя бы одного наставника')
        if not major_codes or not all(code.strip() for code in major_codes):
            errors.append('Добавьте хотя бы одно направление обучения')
        if not major_profiles or not all(profile.strip() for profile in major_profiles):
            errors.append('Добавьте описание для всех направлений')
        if not partners or not all(partner.strip() for partner in partners):
            errors.append('Добавьте хотя бы одного заказчика/партнера')
        if not participants or not all(p.strip() for p in participants):
            errors.append('Добавьте хотя бы одного участника проекта')

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('admin_forms'))

        conn = get_db_connection()
        saved_paths = []

        try:
            cur = conn.cursor()

            logo_file = request.files.get('logo')
            logo_storage_name = None

            if logo_file and logo_file.filename:
                if logo_file.mimetype.startswith('image/'):
                    orig_raw = logo_file.filename
                    orig = secure_filename(orig_raw)
                    if not orig:
                        _, ext = os.path.splitext(orig_raw)
                        orig = f"logo{ext or ''}"
                    unique = f"logo_{uuid.uuid4().hex}_{orig}"
                    path = os.path.join(UPLOAD_FOLDER, unique)
                    logo_file.save(path)
                    logo_storage_name = unique
                    saved_paths.append(path)
                else:
                    flash('Логотип должен быть изображением', 'warning')

            cur.execute("""
                INSERT INTO projects (title, short_description, description, 
                                     logo_storage_name, status) 
                VALUES (?, ?, ?, ?, 'posted')
            """, (title, short_description, description, logo_storage_name))
            project_id = cur.lastrowid

            for dept in departments:
                if dept.strip():
                    cur.execute("INSERT INTO project_departments (project_id, department_name) VALUES (?, ?)",
                                (project_id, dept.strip()))

            for mentor in mentors:
                if mentor.strip():
                    cur.execute("INSERT INTO project_mentors (project_id, mentor_name) VALUES (?, ?)",
                                (project_id, mentor.strip()))

            for participant in participants:
                if participant.strip():
                    cur.execute("INSERT INTO project_participants (project_id, participant_name) VALUES (?, ?)",
                                (project_id, participant.strip()))

            for code, profile in zip(major_codes, major_profiles):
                if code.strip() and profile.strip():
                    cur.execute("INSERT INTO project_majors (project_id, major_code, major_profile) VALUES (?, ?, ?)",
                                (project_id, code.strip(), profile.strip()))

            for partner in partners:
                if partner.strip():
                    cur.execute("INSERT INTO project_partners (project_id, partner_name) VALUES (?, ?)",
                                (project_id, partner.strip()))

            project_files = request.files.getlist('project_files[]')
            for f in project_files:
                if f and getattr(f, 'filename', None) and f.filename.strip():
                    orig_raw = f.filename
                    orig = secure_filename(orig_raw)
                    if not orig:
                        _, ext = os.path.splitext(orig_raw)
                        orig = f"file{ext or ''}"
                    unique = f"{uuid.uuid4().hex}_{orig}"
                    path = os.path.join(UPLOAD_FOLDER, unique)
                    f.save(path)
                    saved_paths.append(path)
                    cur.execute("""
                        INSERT INTO project_files (project_id, filename, storage_name, mime_type) 
                        VALUES (?, ?, ?, ?)
                    """, (project_id, orig, unique, f.mimetype))

            for tag_id in selected_tags:
                try:
                    tag_id_int = int(tag_id)
                    cur.execute("INSERT INTO project_tags (project_id, tag_id) VALUES (?,?)",
                                (project_id, tag_id_int))
                except Exception as e:
                    print(f"Ошибка при добавлении тега {tag_id}: {e}")

            if custom_tag.strip():
                try:
                    cur.execute(
                        "INSERT INTO suggested_tags (project_id, name, status) VALUES (?, ?, 'pending')",
                        (project_id, custom_tag.strip())
                    )
                except Exception as e:
                    print(f"Ошибка при добавлении предложенного тега: {e}")

            conn.commit()
            flash(f'Проект "{title}" успешно создан и опубликован на витрине! ID: {project_id}', 'success')

        except Exception as e:
            conn.rollback()
            print(f"Ошибка БД: {e}")
            import traceback
            traceback.print_exc()

            for p in saved_paths:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except:
                    pass

            flash(f'Ошибка при создании проекта: {str(e)}', 'error')
            return redirect(url_for('admin_forms'))
        finally:
            conn.close()

    except Exception as e:
        print(f"Общая ошибка: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Ошибка при обработке формы: {str(e)}', 'error')
        return redirect(url_for('admin_forms'))

    return redirect(url_for('admin'))


@app.route("/admin")
def admin():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    status_filter = request.args.get('status', 'moderation')
    conn = get_db_connection()
    cur = conn.cursor()

    if status_filter == 'all':
        query = """
            SELECT p.id, p.title, p.short_description, p.description, p.logo_storage_name, 
                p.status, p.created_at, -- Добавьте эту строку
                GROUP_CONCAT(t.name, ',') as tags
            FROM projects p
            LEFT JOIN project_tags ptg ON p.id = ptg.project_id
            LEFT JOIN tags t ON ptg.tag_id = t.id
            GROUP BY p.id
            ORDER BY p.id DESC
        """
        params = []
    else:
        query = """
            SELECT p.id, p.title, p.short_description, p.description, p.logo_storage_name, 
                   p.status,
                   GROUP_CONCAT(t.name, ',') as tags
            FROM projects p
            LEFT JOIN project_tags ptg ON p.id = ptg.project_id
            LEFT JOIN tags t ON ptg.tag_id = t.id
            WHERE p.status = ?
            GROUP BY p.id
            ORDER BY p.id DESC
        """
        params = [status_filter]

    cur.execute(query, params)
    projects = cur.fetchall()
    conn.close()

    projects_list = []
    for p in projects:
        p_dict = dict(p)
        if p_dict.get('tags'):
            tags_str = p_dict['tags'] if p_dict['tags'] else ''
            p_dict['tags'] = [{'name': t.strip()} for t in tags_str.split(',') if t.strip()]
        else:
            p_dict['tags'] = []

        projects_list.append(p_dict)

    return render_template("admin.html", projects=projects_list, status_filter=status_filter)


@app.route("/admin/project/<int:project_id>/approve", methods=["POST"])
def admin_approve(project_id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE projects SET status = 'posted' WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    flash('Проект одобрен и опубликован!', 'success')
    return redirect(url_for('admin', status='moderation'))


@app.route("/admin/project/<int:project_id>/post", methods=["POST"])
def admin_post(project_id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE projects SET status = 'posted' WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', status='posted'))


@app.route("/admin/project/<int:project_id>/hide", methods=["POST"])
def admin_hide(project_id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE projects SET status = 'hidden' WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', status='hidden'))


@app.route("/admin/project/<int:project_id>/unpost", methods=["POST"])
def admin_unpost(project_id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE projects SET status = 'pending' WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin', status='pending'))


@app.route("/admin/project/<int:project_id>/delete", methods=["POST"])
def admin_delete(project_id):
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT storage_name FROM project_files WHERE project_id = ?", (project_id,))
    files = cur.fetchall()
    cur.execute("SELECT logo_storage_name FROM projects WHERE id = ?", (project_id,))
    logo = cur.fetchone()

    cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()

    upload_folder = app.config['UPLOAD_FOLDER']
    for file in files:
        try:
            file_path = os.path.join(upload_folder, file['storage_name'])
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

    if logo and logo['logo_storage_name']:
        try:
            logo_path = os.path.join(upload_folder, logo['logo_storage_name'])
            if os.path.exists(logo_path):
                os.remove(logo_path)
        except Exception as e:
            print(f"Error deleting logo: {e}")

    conn.close()
    flash('Проект успешно удален!', 'success')
    return redirect(url_for('admin'))


@app.route('/project/<int:project_id>', methods=['GET'])
def project_view(project_id):
    conn = get_db_connection()
    cur = conn.cursor()

    is_admin = is_admin_logged_in()

    if is_admin:
        cur.execute("""
            SELECT p.*
            FROM projects p
            WHERE p.id = ?
        """, (project_id,))
    else:
        cur.execute("""
            SELECT p.*
            FROM projects p
            WHERE p.id = ? AND p.status = 'posted'
        """, (project_id,))

    proj = cur.fetchone()
    if not proj:
        abort(404)

    proj_dict = dict(proj)

    cur.execute("""
        SELECT t.name 
        FROM tags t
        JOIN project_tags ptg ON t.id = ptg.tag_id
        WHERE ptg.project_id = ?
    """, (project_id,))
    proj_dict['tags'] = [{'name': row['name']} for row in cur.fetchall()]

    cur.execute("SELECT department_name FROM project_departments WHERE project_id = ?", (project_id,))
    departments = cur.fetchall()
    proj_dict['department_name'] = ', '.join([d['department_name'] for d in departments]) if departments else 'Не указано'

    cur.execute("SELECT mentor_name FROM project_mentors WHERE project_id = ?", (project_id,))
    mentors = cur.fetchall()
    proj_dict['mentor_name'] = ', '.join([m['mentor_name'] for m in mentors]) if mentors else 'Не указано'

    cur.execute("""
        SELECT participant_name 
        FROM project_participants 
        WHERE project_id = ?
        ORDER BY id
    """, (project_id,))
    participants = [{'participant_name': row['participant_name']} for row in cur.fetchall()]

    cur.execute("SELECT major_code, major_profile FROM project_majors WHERE project_id = ?", (project_id,))
    majors = cur.fetchall()
    if majors:
        proj_dict['major_code'] = ', '.join([m['major_code'] for m in majors])
        proj_dict['major_profile'] = ', '.join([m['major_profile'] for m in majors])
    else:
        proj_dict['major_code'] = 'Не указано'
        proj_dict['major_profile'] = 'Не указано'

    cur.execute("SELECT partner_name FROM project_partners WHERE project_id = ?", (project_id,))
    partners = cur.fetchall()
    proj_dict['partner_name'] = ', '.join([p['partner_name'] for p in partners]) if partners else 'Не указано'

    cur.execute("""
        SELECT filename, storage_name, mime_type 
        FROM project_files 
        WHERE project_id = ?
        ORDER BY id
    """, (project_id,))
    files = cur.fetchall()
    conn.close()

    return render_template('project.html',
                           project=proj_dict,
                           participants=participants,
                           files=files,
                           is_admin=is_admin)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)