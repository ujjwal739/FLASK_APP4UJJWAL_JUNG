from database import get_db

def get_all_resources(category_id=None, resource_type=None, approved_only=True):
    conn = get_db()
    query = '''
        SELECT r.*, c.name as category_name, c.icon as category_icon
        FROM resources r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE 1=1
    '''
    params = []
    if approved_only:
        query += ' AND r.approved = 1'
    if category_id:
        query += ' AND r.category_id = ?'
        params.append(category_id)
    if resource_type:
        query += ' AND r.resource_type = ?'
        params.append(resource_type)
    query += ' ORDER BY r.created_at DESC'
    resources = conn.execute(query, params).fetchall()
    conn.close()
    return resources

def get_resource_by_id(res_id):
    conn = get_db()
    res = conn.execute('''
        SELECT r.*, c.name as category_name FROM resources r
        LEFT JOIN categories c ON r.category_id = c.id WHERE r.id=?
    ''', (res_id,)).fetchone()
    conn.close()
    return res

def create_resource(title, url, description, resource_type, category_id, submitted_by, approved=1):
    conn = get_db()
    conn.execute('''INSERT INTO resources (title, url, description, resource_type, category_id, submitted_by, approved)
        VALUES (?,?,?,?,?,?,?)''', (title, url, description, resource_type, category_id or None, submitted_by, approved))
    conn.commit()
    conn.close()

def update_resource(res_id, title, url, description, resource_type, category_id, approved):
    conn = get_db()
    conn.execute('''UPDATE resources
        SET title=?, url=?, description=?, resource_type=?, category_id=?, approved=?
        WHERE id=?''', (title, url, description, resource_type, category_id or None, approved, res_id))
    conn.commit()
    conn.close()

def toggle_resource_approval(res_id):
    conn = get_db()
    conn.execute('UPDATE resources SET approved = CASE WHEN approved=1 THEN 0 ELSE 1 END WHERE id=?', (res_id,))
    conn.commit()
    conn.close()

def delete_resource(res_id):
    conn = get_db()
    conn.execute('DELETE FROM resources WHERE id=?', (res_id,))
    conn.commit()
    conn.close()

def get_pending_resources():
    conn = get_db()
    resources = conn.execute('''
        SELECT r.*, c.name as category_name FROM resources r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.approved = 0 ORDER BY r.created_at DESC
    ''').fetchall()
    conn.close()
    return resources
