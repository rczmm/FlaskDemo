from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, abort
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = '34daEWWE15fdfsadadawe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/buy'
db = SQLAlchemy(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'buy'
mysql = MySQL(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    cart_items = db.relationship("ShoppingCart", backref="user", lazy=True)
    liked_products = db.relationship('Like', backref='user', lazy=True)


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    liked_by_users = db.relationship('Like', backref='product', lazy=True)


class ShoppingCart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Like(db.Model):
    like_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)


products = [
    {'id': 1, 'name': 'Product 1', 'price': 10.99},
    {'id': 2, 'name': 'Product 2', 'price': 9.99},
    {'id': 3, 'name': 'Product 3', 'price': 12.99}
]


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('search.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        print(user)
        if user:
            print("登录成功！")
            session['user_id'] = user.user_id
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    print(session)
    if 'user_id' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        query = request.form['query']
        results = db.session.query(Product).filter(Product.name.like('%{}%'.format(query))).all()
        results_with_url = [
            {'name': product.name, 'price': product.price, 'url': url_for('product', product_id=product.product_id)} for product
            in results]
        return render_template('search.html', results=results_with_url)
    return render_template('search.html')


@app.route('/product/<int:product_id>')
def product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    product = Product.query.get(product_id)
    if product:
        liked = Like.query.filter_by(user_id=session['user_id'], product_id=product_id).first() is not None
        print(product,liked)
        return render_template('product.html', product=product, liked=liked, product_id=product_id)
    return 'Product not found', 404


@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    return render_template('cart.html')


@app.route('/get_cart')
def cart_items():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    cart_items = db.session.query(ShoppingCart, Product).join(Product,
                                                              ShoppingCart.product_id == Product.product_id).all()
    total_price = sum(item.Product.price * item.ShoppingCart.quantity for item in cart_items)
    cart = [{'name': item.Product.name, 'quantity': item.ShoppingCart.quantity, 'price': item.Product.price} for item in
            cart_items]
    return jsonify({'cart': cart, 'total_price': total_price})


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM shopping_cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    cart_item = cur.fetchone()
    if cart_item:
        cur.execute("UPDATE shopping_cart SET quantity = quantity + 1 WHERE cart_id = '{}'".format(cart_item[0]))
    else:
        cur.execute("INSERT INTO shopping_cart (user_id, product_id, quantity) VALUES (%s, %s, 1)",
                    (user_id, product_id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('cart'))


@app.route('/toggle_like/<int:product_id>', methods=['POST'])
def toggle_like(product_id):
    if 'user_id' not in session:
        abort(403)
    user_id = session['user_id']
    like = Like.query.filter_by(user_id=user_id, product_id=product_id).first()
    print(like)
    if like:
        db.session.delete(like)
        liked = False
    else:
        new_like = Like(user_id=user_id, product_id=product_id)
        db.session.add(new_like)
        liked = True
    db.session.commit()
    return jsonify({'liked': liked})


if __name__ == '__main__':
    app.run(debug=True)
