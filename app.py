import os
import sqlite3
import subprocess
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Папка куда будут сохраняться картинки
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Максимальный размер файла — 5 мегабайт
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# Разрешённые форматы картинок
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Функция для подключения к базе данных
def get_db():
    conn = sqlite3.connect('cards.db')
    conn.row_factory = sqlite3.Row
    return conn

# Создаём таблицу если её ещё нет
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

# Главная страница — показываем все карточки
@app.route('/')
def index():
    conn = get_db()
    cards = conn.execute('SELECT * FROM cards').fetchall()
    conn.close()
    return render_template('index.html', cards=cards)

# Страница с формой добавления
@app.route('/add')
def add():
    return render_template('add.html')

# Обработка отправки формы
@app.route('/upload', methods=['POST'])
def upload():
    card_text = request.form['card_text']
    card_image = request.files['card_image']

    # Проверяем что файл является картинкой
    if not allowed_file(card_image.filename):
        return 'Можно загружать только картинки!', 400

    # Делаем имя файла безопасным
    image_filename = secure_filename(card_image.filename)

    # Сохраняем картинку в папку static/uploads
    card_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    # Сохраняем текст и имя файла в базу данных
    conn = get_db()
    conn.execute('INSERT INTO cards (text, image) VALUES (?, ?)', (card_text, image_filename))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
