from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = "super-secret-key-for-social-media" # നിങ്ങളുടെ ആപ്പിന്റെ സുരക്ഷയ്ക്ക്

# ഗൂഗിൾ ലോഗിൻ സെറ്റപ്പ് (OAuth)
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='YOUR_GOOGLE_CLIENT_ID', # ഇത് നമ്മൾ അടുത്ത സ്റ്റെപ്പിൽ എടുക്കും
    client_secret='YOUR_GOOGLE_CLIENT_SECRET', # ഇതും അടുത്ത സ്റ്റെപ്പിൽ എടുക്കും
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            content TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    # ലോഗിൻ ചെയ്തിട്ടുണ്ടോ എന്ന് നോക്കുന്നു
    user = session.get('user')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, content, email FROM posts ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    feed_posts = [{"id": row[0], "username": row[1], "content": row[2], "email": row[3]} for row in rows]
    return render_template('index.html', posts=feed_posts, current_user=user)

# ഗൂഗിളിലേക്ക് റീഡയറക്ട് ചെയ്യുന്ന വഴി
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_uri)

# ലോഗിൻ കഴിഞ്ഞു തിരിച്ചു വരുമ്പോൾ ഉള്ള വഴി
@app.route('/auth')
def auth():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    # യൂസറുടെ വിവരങ്ങൾ സെഷനിൽ സൂക്ഷിക്കുന്നു
    session['user'] = user_info
    return redirect('/')

# ലോഗ് ഔട്ട് ചെയ്യാനുള്ള വഴി
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/post', methods=['POST'])
def create_post():
    user = session.get('user')
    if not user:
        return redirect(url_for('home')) # ലോഗിൻ ചെയ്തില്ലെങ്കിൽ പോസ്റ്റ് ഇടാൻ പറ്റില്ല
        
    text = request.form.get('content')
    if text:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # യഥാർത്ഥ ഗൂഗിൾ പേരും ഇമെയിലും മാത്രം ഡാറ്റാബേസിലേക്ക് കയറ്റുന്നു
        cursor.execute('INSERT INTO posts (username, content, email) VALUES (?, ?, ?)', 
                       (user['name'], text, user['email']))
        conn.commit()
        conn.close()
        
    return redirect(url_for('home'))

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('home'))
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # സുരക്ഷ: സ്വന്തം പോസ്റ്റുകൾ മാത്രമേ ഡിലീറ്റ് ചെയ്യാൻ അനുവദിക്കൂ
    cursor.execute('SELECT email FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    
    if post and post[0] == user['email']:
        cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
