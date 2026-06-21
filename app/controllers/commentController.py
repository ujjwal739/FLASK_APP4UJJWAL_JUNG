from database import get_db

def get_comments_for_tip(tip_id):
    conn = get_db()
    comments = conn.execute(
        'SELECT * FROM comments WHERE tip_id=? AND approved=1 ORDER BY created_at DESC',
        (tip_id,)
    ).fetchall()
    conn.close()
    return comments

def get_all_comments():
    conn = get_db()
    comments = conn.execute('''
        SELECT cm.*, t.title as tip_title FROM comments cm
        LEFT JOIN tips t ON cm.tip_id = t.id
        ORDER BY cm.created_at DESC
    ''').fetchall()
    conn.close()
    return comments

def add_comment(tip_id, author_name, content):
    conn = get_db()
    conn.execute(
        'INSERT INTO comments (tip_id, author_name, content) VALUES (?,?,?)',
        (tip_id, author_name, content)
    )
    conn.commit()
    conn.close()

def update_comment(comment_id, author_name, content):
    conn = get_db()
    conn.execute(
        'UPDATE comments SET author_name=?, content=? WHERE id=?',
        (author_name, content, comment_id)
    )
    conn.commit()
    conn.close()

def delete_comment(comment_id):
    conn = get_db()
    conn.execute('DELETE FROM comments WHERE id=?', (comment_id,))
    conn.commit()
    conn.close()

def toggle_approve(comment_id):
    conn = get_db()
    conn.execute(
        'UPDATE comments SET approved = CASE WHEN approved=1 THEN 0 ELSE 1 END WHERE id=?',
        (comment_id,)
    )
    conn.commit()
    conn.close()
