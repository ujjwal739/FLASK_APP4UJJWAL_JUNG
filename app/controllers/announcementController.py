from database import get_db
from datetime import date

def get_active_announcements():
    conn = get_db()
    today = date.today().isoformat()
    announcements = conn.execute('''
        SELECT * FROM announcements
        WHERE is_active = 1 AND (expires_at IS NULL OR expires_at >= ?)
        ORDER BY CASE severity
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'warning' THEN 3
            ELSE 4 END, created_at DESC
    ''', (today,)).fetchall()
    conn.close()
    return announcements

def get_all_announcements():
    conn = get_db()
    announcements = conn.execute(
        'SELECT * FROM announcements ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return announcements

def get_announcement_by_id(ann_id):
    conn = get_db()
    ann = conn.execute('SELECT * FROM announcements WHERE id=?', (ann_id,)).fetchone()
    conn.close()
    return ann

def create_announcement(title, content, severity, expires_at, created_by):
    conn = get_db()
    conn.execute('''INSERT INTO announcements (title, content, severity, is_active, expires_at, created_by)
        VALUES (?,?,?,1,?,?)''', (title, content, severity, expires_at or None, created_by))
    conn.commit()
    conn.close()

def update_announcement(ann_id, title, content, severity, expires_at, is_active):
    conn = get_db()
    conn.execute('''UPDATE announcements
        SET title=?, content=?, severity=?, expires_at=?, is_active=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?''', (title, content, severity, expires_at or None, is_active, ann_id))
    conn.commit()
    conn.close()

def toggle_announcement(ann_id):
    conn = get_db()
    conn.execute('UPDATE announcements SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END WHERE id=?', (ann_id,))
    conn.commit()
    conn.close()

def delete_announcement(ann_id):
    conn = get_db()
    conn.execute('DELETE FROM announcements WHERE id=?', (ann_id,))
    conn.commit()
    conn.close()
