from database import get_db

def get_all_categories():
    conn = get_db()
    cats = conn.execute('''
        SELECT c.*, COUNT(t.id) as tip_count
        FROM categories c LEFT JOIN tips t ON c.id = t.category_id
        GROUP BY c.id ORDER BY c.name
    ''').fetchall()
    conn.close()
    return cats

def get_category_by_id(cat_id):
    conn = get_db()
    cat = conn.execute('SELECT * FROM categories WHERE id=?', (cat_id,)).fetchone()
    conn.close()
    return cat

def create_category(name, description, icon):
    conn = get_db()
    conn.execute(
        'INSERT INTO categories (name, description, icon) VALUES (?,?,?)',
        (name, description, icon)
    )
    conn.commit()
    conn.close()

def update_category(cat_id, name, description, icon):
    conn = get_db()
    conn.execute(
        'UPDATE categories SET name=?, description=?, icon=? WHERE id=?',
        (name, description, icon, cat_id)
    )
    conn.commit()
    conn.close()

def delete_category(cat_id):
    conn = get_db()
    conn.execute('DELETE FROM categories WHERE id=?', (cat_id,))
    conn.commit()
    conn.close()
