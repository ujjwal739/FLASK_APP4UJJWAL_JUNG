from database import get_db

def get_all_tips(category_id=None, severity=None):
    conn = get_db()
    query = '''
        SELECT t.*, c.name as category_name, c.icon as category_icon
        FROM tips t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    '''
    params = []
    if category_id:
        query += ' AND t.category_id = ?'
        params.append(category_id)
    if severity:
        query += ' AND t.severity = ?'
        params.append(severity)
    query += ' ORDER BY t.created_at DESC'
    tips = conn.execute(query, params).fetchall()
    conn.close()
    return tips

def get_tip_by_id(tip_id):
    conn = get_db()
    tip = conn.execute('''
        SELECT t.*, c.name as category_name, c.icon as category_icon
        FROM tips t LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    ''', (tip_id,)).fetchone()
    conn.close()
    return tip

def create_tip(title, content, category_id, severity):
    conn = get_db()
    conn.execute(
        'INSERT INTO tips (title, content, category_id, severity) VALUES (?,?,?,?)',
        (title, content, category_id, severity)
    )
    conn.commit()
    conn.close()

def update_tip(tip_id, title, content, category_id, severity):
    conn = get_db()
    conn.execute('''
        UPDATE tips SET title=?, content=?, category_id=?, severity=?,
        updated_at=CURRENT_TIMESTAMP WHERE id=?
    ''', (title, content, category_id, severity, tip_id))
    conn.commit()
    conn.close()

def delete_tip(tip_id):
    conn = get_db()
    conn.execute('DELETE FROM comments WHERE tip_id=?', (tip_id,))
    conn.execute('DELETE FROM tips WHERE id=?', (tip_id,))
    conn.commit()
    conn.close()
