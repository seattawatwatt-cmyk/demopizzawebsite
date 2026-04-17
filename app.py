from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('pizza.db')
    conn.row_factory = sqlite3.Row
    return conn


SAMPLE_PIZZAS = [
    ('Margherita', 250, 'https://i.pinimg.com/736x/4a/30/2d/4a302dfc09462c5009555e876e6c5b39.jpg', 12, 1),
    ('Pepperoni Passion', 320, 'https://i.pinimg.com/736x/45/07/6f/45076f24d6ca9d75f66f78ab948d7345.jpg', 8, 2),
    ('Hawaiian Delight', 290, 'https://i.pinimg.com/736x/45/b3/29/45b32937fd120e000ab568c5c1b0caf5.jpg', 6, 2),
    ('Garden Fresh', 260, 'https://i.pinimg.com/736x/08/c7/90/08c790d732aa6b813a66dd622ff8319c.jpg', 9, 3),
    ('BBQ Chicken', 345, 'https://i.pinimg.com/736x/fc/e3/ec/fce3ec6c8b636debf0f5ce9b5f2fa7b6.jpg', 7, 2),
    ('Four Cheese', 310, 'https://i.pinimg.com/736x/48/bd/91/48bd91b29f145171581445673e84c5bf.jpg', 10, 1),
    ('Shrimp Fiesta', 340, 'https://i.pinimg.com/736x/a1/b5/a1/a1b5a1cb22c5ae0d4382acd735eca98b.jpg', 7, 2),
    ('Corn Delight', 275, 'https://i.pinimg.com/736x/9a/b2/06/9ab2067ed1e3ef3482b1990cffb8b38c.jpg', 11, 3),
]

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pizza (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            image TEXT,
            stock INTEGER NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    conn.execute("INSERT OR IGNORE INTO categories (id, name) VALUES (1, 'Classic'), (2, 'Spicy'), (3, 'Vegetarian')")
    conn.commit()

    conn.execute('DELETE FROM pizza')
    for pizza in SAMPLE_PIZZAS:
        conn.execute(
            'INSERT INTO pizza (name, price, image, stock, category_id) VALUES (?, ?, ?, ?, ?)',
            pizza
        )
    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    conn = get_db_connection()
    pizzas = conn.execute('''
        SELECT pizza.*, categories.name AS category_name
        FROM pizza
        JOIN categories ON pizza.category_id = categories.id
        GROUP BY pizza.name
        ORDER BY MIN(pizza.id) ASC
        LIMIT 8
    ''').fetchall()
    conn.close()
    return render_template('index.html', pizzas=pizzas)


@app.route('/add', methods=['GET', 'POST'])
def add():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        stock = request.form['stock']
        category_id = request.form['category_id']
        conn.execute(
            'INSERT INTO pizza (name, price, image, stock, category_id) VALUES (?, ?, ?, ?, ?)',
            (name, price, image, stock, category_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return render_template('add.html', categories=categories)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    pizza = conn.execute('SELECT * FROM pizza WHERE id = ?', (id,)).fetchone()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        stock = request.form['stock']
        category_id = request.form['category_id']
        conn.execute(
            'UPDATE pizza SET name = ?, price = ?, image = ?, stock = ?, category_id = ? WHERE id = ?',
            (name, price, image, stock, category_id, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return render_template('edit.html', pizza=pizza, categories=categories)


@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM pizza WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
