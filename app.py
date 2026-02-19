import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Папка куда будут сохраняться картинки
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

    # Сохраняем картинку в папку static/uploads
    image_filename = card_image.filename
    card_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    # Сохраняем текст и имя файла в базу данных
    conn = get_db()
    conn.execute('INSERT INTO cards (text, image) VALUES (?, ?)', (card_text, image_filename))
    conn.commit()
    conn.close()

    # После загрузки отправляем пользователя на главную страницу
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)