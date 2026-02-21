import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    conn = sqlite3.connect('cards.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            image TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    cards = conn.execute('SELECT * FROM cards').fetchall()
    conn.close()
    return render_template('index.html', cards=cards)

@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/upload', methods=['POST'])
def upload():
    card_text = request.form['card_text']
    card_image = request.files['card_image']

    if not allowed_file(card_image.filename):
        return 'Можно загружать только картинки!', 400

    image_filename = secure_filename(card_image.filename)
    card_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    conn = get_db()
    conn.execute('INSERT INTO cards (text, image) VALUES (?, ?)', (card_text, image_filename))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/delete/<int:card_id>', methods=['POST'])
def delete(card_id):
    conn = get_db()

    card = conn.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], card['image'])
    if os.path.exists(image_path):
        os.remove(image_path)

    conn.execute('DELETE FROM cards WHERE id = ?', (card_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
