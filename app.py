from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# പോസ്റ്റുകൾ താല്ക്കാലികമായി സൂക്ഷിച്ചുവെക്കാനുള്ള ഒരു ലിസ്റ്റ് (Database-ന് പകരം)
feed_posts = [
    {"username": "ആദി", "content": "ഹലോ കൂട്ടുകാരേ, എന്റെ പുതിയ സോഷ്യൽ മീഡിയയിലേക്ക് സ്വാഗതം!"},
    {"username": "അച്ചു", "content": "ഇത് വളരെ മികച്ചൊരു ആശയമാണ്, ആശംസകൾ!"}
]

@app.route('/')
def home():
    return render_template('index.html', posts=feed_posts)

@app.route('/post', methods=['POST'])
def create_post():
    user = request.form.get('username')
    text = request.form.get('content')
    
    if user and text:
        # പുതിയ പോസ്റ്റ് ലിസ്റ്റിലേക്ക് ചേർക്കുന്നു
        feed_posts.insert(0, {"username": user, "content": text})
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
