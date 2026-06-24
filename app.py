from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ഇതിന് തൊട്ടുതാഴെയുള്ള വരി ചേർക്കുക
init_db()
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # ഇവിടെ AUTOINCREMENT സ്പേസ് ഇല്ലാതെ തിരുത്തിയിട്ടുണ്ട്
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, content FROM posts ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    feed_posts = [{"id": row[0], "username": row[1], "content": row[2]} for row in rows]
    return render_template('index.html', posts=feed_posts)

@app.route('/post', methods=['POST'])
def create_post():
    user = request.form.get('username')
    text = request.form.get('content')
    
    if user and text:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (username, content) VALUES (?, ?)', (user, text))
        conn.commit()
        conn.close()
        
    return redirect(url_for('home'))

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
