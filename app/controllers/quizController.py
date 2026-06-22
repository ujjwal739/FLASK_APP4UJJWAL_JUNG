from database import get_db

def get_all_questions(category_id=None, difficulty=None):
    conn = get_db()
    query = '''
        SELECT q.*, c.name as category_name
        FROM quiz_questions q
        LEFT JOIN categories c ON q.category_id = c.id
        WHERE 1=1
    '''
    params = []
    if category_id:
        query += ' AND q.category_id = ?'
        params.append(category_id)
    if difficulty:
        query += ' AND q.difficulty = ?'
        params.append(difficulty)
    query += ' ORDER BY q.created_at DESC'
    questions = conn.execute(query, params).fetchall()
    conn.close()
    return questions

def get_question_by_id(question_id):
    conn = get_db()
    q = conn.execute('''
        SELECT q.*, c.name as category_name FROM quiz_questions q
        LEFT JOIN categories c ON q.category_id = c.id WHERE q.id=?
    ''', (question_id,)).fetchone()
    conn.close()
    return q

def create_question(data):
    conn = get_db()
    conn.execute('''
        INSERT INTO quiz_questions
        (question, option_a, option_b, option_c, option_d, correct_option, explanation, category_id, difficulty)
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', (data['question'], data['option_a'], data['option_b'], data['option_c'],
          data['option_d'], data['correct_option'], data.get('explanation',''),
          data.get('category_id'), data.get('difficulty','medium')))
    conn.commit()
    conn.close()

def update_question(question_id, data):
    conn = get_db()
    conn.execute('''
        UPDATE quiz_questions SET question=?, option_a=?, option_b=?, option_c=?, option_d=?,
        correct_option=?, explanation=?, category_id=?, difficulty=? WHERE id=?
    ''', (data['question'], data['option_a'], data['option_b'], data['option_c'],
          data['option_d'], data['correct_option'], data.get('explanation',''),
          data.get('category_id'), data.get('difficulty','medium'), question_id))
    conn.commit()
    conn.close()

def delete_question(question_id):
    conn = get_db()
    conn.execute('DELETE FROM quiz_questions WHERE id=?', (question_id,))
    conn.commit()
    conn.close()

def check_answer(question_id, selected):
    conn = get_db()
    q = conn.execute('SELECT correct_option, explanation FROM quiz_questions WHERE id=?', (question_id,)).fetchone()
    conn.close()
    if not q:
        return None
    return {'correct': q['correct_option'] == selected, 'explanation': q['explanation'], 'correct_option': q['correct_option']}
