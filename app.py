from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# --- Проверяем и создаём папку instance ---
if not os.path.exists('instance'):
    os.makedirs('instance')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- MODELS ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image = db.Column(db.String(100))  # путь к изображению

# ---------- ROUTES ----------
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован.')
            return redirect(url_for('register'))

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        flash('Неверные данные для входа')
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart_items = []
    total = 0
    product_ids = session.get('cart', [])

    if product_ids:
        cart_items = Product.query.filter(Product.id.in_(product_ids)).all()
        total = sum(p.price for p in cart_items)

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    flash('Товар добавлен в корзину!')
    return redirect(url_for('product_detail', product_id=product_id))

# ---------- MAIN ----------
if __name__ == '__main__':
    db_path = 'instance/site.db'
    if not os.path.exists(db_path):
        open(db_path, 'a').close()  # Создаст пустой файл
    with app.app_context():
        db.create_all()
        if not Product.query.first():
            db.session.add_all([
                Product(
                    name="Apple iPhone 16 Pro",
                    description="Флагман Apple с A18 Pro, камерой 48 МП + лидар, ProMotion 120 Гц, iOS 18.",
                    price=89700,
                    image="images/Apple iPhone 16 Pro.png"
                ),
                Product(
                    name="OnePlus 12",
                    description="Snapdragon 8 Gen 3, экран 120 Гц, Hasselblad, зарядка 100 Вт.",
                    price=60800,
                    image="images/OnePlus 12.png"
                ),
                Product(
                    name="Google Pixel 6 Pro",
                    description="Google Tensor, 120 Гц OLED, камера 50 МП + телефото, чистый Android.",
                    price=24990,
                    image="images/Google Pixel 6 Pro.png"
                ),
                Product(
                    name="Samsung Galaxy S23 Ultra",
                    description="Snapdragon 8 Gen 2, 200 МП камера, S-Pen, AMOLED 120 Гц.",
                    price=63500,
                    image="images/ Galaxy S23 Ultra.png"
                ),
                Product(
                    name="Vivo X200 Pro",
                    description="Dimensity 9400, Zeiss камера, 120 Гц AMOLED, зарядка 120 Вт.",
                    price=51351,
                    image="images/Vivo X200 Pro.png"
                ),
                Product(
                    name="Vivo iQOO Neo 10 Pro",
                    description="Snapdragon 8+ Gen 1, 144 Гц экран, охлаждение, зарядка 120 Вт.",
                    price=28453,
                    image="images/ iQOO Neo 10 Pro.png"
                ),
                Product(
                    name="Realme GT Neo 6",
                    description="Snapdragon 8s Gen 3, AMOLED 144 Гц, зарядка 100 Вт, 50 МП камера.",
                    price=20532,
                    image="images/Realme GT Neo 6.jpg"
                ),
                Product(
                    name="Oppo Find X7 Ultra",
                    description="Snapdragon 8 Gen 3, Hasselblad, LTPO 120 Гц, зарядка 100 Вт.",
                    price=54000,
                    image="images/Oppo Find X7 Ultra.jpg"
                ),
                Product(
                    name="Xiaomi 15 Ultra",
                    description="Snapdragon 8 Elite, Leica камера, AMOLED 120 Гц, зарядка 120 Вт.",
                    price=93500,
                    image="images/Xiaomi 15 Ultra.png"
                ),
            ])
            db.session.commit()
        # with app.app_context():
        #     Product(name="Apple iPhone 16 Pro", description="Флагман Apple с A18 Pro, камерой 48 МП + лидар, ProMotion 120 Гц, iOS 18.", price=89700, image="images/Apple iPhone 16 Pro"),
        #     Product(name="OnePlus 12", description="Snapdragon 8 Gen 3, экран 120 Гц, Hasselblad, зарядка 100 Вт.", price=60800, image="images/OnePlus 12.png"),
        #     Product(name="Google Pixel 6 Pro", description="Google Tensor, 120 Гц OLED, камера 50 МП + телефото, чистый Android.", price=24990, image="images/Google Pixel 6 Pro"),
        #     Product(name="Samsung Galaxy S23 Ultra", description="Snapdragon 8 Gen 2, 200 МП камера, S-Pen, AMOLED 120 Гц.", price=63500, image="images/Samsung Galaxy S23 Ultra"),
        #     Product(name="Vivo X200 Pro", description="Dimensity 9400, Zeiss камера, 120 Гц AMOLED, зарядка 120 Вт.", price=51351, image="images/Vivo X200 Pro"),
        #     Product(name="Vivo iQOO Neo 10 Pro", description="Snapdragon 8+ Gen 1, 144 Гц экран, охлаждение, зарядка 120 Вт.", price=28453, image="images/Vivo iQOO Neo 10 Pro"),
        #     Product(name="Realme GT Neo 6", description="Snapdragon 8s Gen 3, AMOLED 144 Гц, зарядка 100 Вт, 50 МП камера.", price=20532, image="images/Realme GT Neo 6"),
        #     Product(name="Oppo Find X7 Ultra", description="Snapdragon 8 Gen 3, Hasselblad, LTPO 120 Гц, зарядка 100 Вт.", price=54000, image="images/Oppo Find X7 Ultra"),
        #     Product(name="Xiaomi 15 Ultra", description="Snapdragon 8 Elite, Leica камера, AMOLED 120 Гц, зарядка 120 Вт.", price=93500, image="images/Xiaomi 15 Ultra"),
        #     db.session.commit()

    app.run(debug=True)
