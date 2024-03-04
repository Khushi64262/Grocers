from flask import render_template, flash, redirect, url_for, request, session
from MAD1.forms import RegistrationForm, LoginForm, ProductForm, CategoryForm
from MAD1.models import User, Category, Product, Cart, Purchase
from MAD1 import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from MAD1 import login_manager
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id = int(user_id)).first()


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created, you can now log in!', 'success')
            return redirect(url_for('login'))
    else:
        form = RegistrationForm()
        return render_template('register.html', form = form)

@app.route('/login_admin',methods = ['GET', 'POST'])
def login_admin():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if form.validate_on_submit() and user.is_admin:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Login Successful as Admin','success')
                return redirect(url_for('home_admin'))
            else:
                flash('Incorrect Password', 'danger')
                return redirect('login')
        else:
            flash('You are not an admin', 'danger')
            return redirect(url_for('login'))
    return render_template('admin_login.html', form = form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if form.validate_on_submit() and not user.is_admin:
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    flash(f'Login Successful as {current_user.username}', 'success')
                    return redirect('home_user')
                else:
                    flash('Incorrent Password', 'danger')
                    return redirect('user_login')
            else:
                flash('You are not an user','danger')
                return redirect('register')
        else:
            flash('User not found with this Email - id','danger')
            return redirect('register')
    return render_template('user_login.html',form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home_user', methods=['GET', 'POST'])
@login_required
def home_user():
    categories = Category.query.all()
    products = Product.query.order_by(Product.created_at.desc()).all()

    return render_template("home_user.html", categories=categories, products=products)

@app.route('/home_admin', methods = ['GET', 'POST', 'PUT'])
@login_required
def home_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('You do not have permission','danger')
        return redirect(url_for('home'))
    return render_template("home_admin.html", current_user=current_user)

@app.route('/category_management', methods=['GET', 'POST'])
@login_required
def category_management():
    categories = Category.query.all()
    products = Product.query.all()
    form = CategoryForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully', 'success')
        return redirect(url_for('category_management'))
    
    return render_template('category_management.html', form=form, categories=categories, products=products)

@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()

    if request.method == 'POST' and form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated successfully', 'success')
        return redirect(url_for('category_management'))
    
    form.name.data = category.name
    return render_template('edit_category.html', form=form, category=category)

@app.route('/delete_category/<int:category_id>', methods=['GET'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    purchases = Purchase.query.filter_by(category_id = category_id).all()
    products_to_delete = Product.query.filter_by(category_id=category.id).all()
    for product in products_to_delete:
        db.session.delete(product)
    for purchase in purchases:
        db.session.delete(purchase)
    db.session.delete(category)
    db.session.commit()

    flash('Category and all associated products deleted successfully', 'success')
    return redirect(url_for('category_management'))

@app.route('/product_management', methods=['GET', 'POST'])
@login_required
def product_management():
    products = Product.query.all()
    categories = Category.query.all()
    form = ProductForm()
    form.category.choices = [(category.id, category.name) for category in categories]

    if request.method == 'POST' and form.validate_on_submit():
        category = Category.query.get(form.category.data)
        product = Product(
            name=form.name.data,
            manufacturer=form.manufacturer.data,
            expiry_date=form.expiry_date.data,
            rate_per_unit=form.rate_per_unit.data,
            unit=form.unit.data,
            units_available = form.units_available.data,
            category=category
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('product_management'))
    
    return render_template('product_management.html', form=form, products=products, categories=categories)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    form = ProductForm()

    form.category.choices = [(category.id, category.name) for category in categories]
    if request.method == 'POST' and form.validate_on_submit():
        selected_category = Category.query.get(form.category.data)

        product.name = form.name.data
        product.manufacturer = form.manufacturer.data
        product.expiry_date = form.expiry_date.data
        product.rate_per_unit = form.rate_per_unit.data
        product.unit = form.unit.data
        product.units_available = form.units_available.data
        product.category = selected_category
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('product_management'))
    elif product.expiry_date < datetime.today().date():
        flash('Product is expired, add some other date', 'danger')

    form.name.data = product.name
    form.manufacturer.data = product.manufacturer
    form.expiry_date.data = product.expiry_date
    form.rate_per_unit.data = product.rate_per_unit
    form.unit.data = product.unit
    form.units_available.data = product.units_available
    form.category.data = product.category.id 

    return render_template('edit_product.html', form=form, product=product, categories=categories)


@app.route('/delete_product/<int:product_id>')
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    purchase = Purchase.query.filter_by(product_id = product_id).first()
    if purchase is not None:
        db.session.delete(purchase)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('product_management'))

def remove_cart_item(cart_item_id):
    cart_item = Cart.query.get(cart_item_id)
    if cart_item and cart_item.user_id == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart', 'success')
    else:
        flash('Item not found in your cart', 'danger')

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    if request.method == 'POST':
        cart_item_id = int(request.form.get('remove_item'))
        remove_cart_item(cart_item_id)
    user_cart = Cart.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.rate_per_unit * item.quantity for item in user_cart)
    return render_template('cart.html', user_cart=user_cart, total_price=total_price)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('home_user'))

    quantity = int(request.form.get('quantity'))
    if quantity <= 0:
        flash('Invalid quantity', 'danger')
        return redirect(url_for('home_user'))

    if product.units_available < quantity:
        flash('Insufficient stock', 'danger')
        return redirect(url_for('home_user'))

    existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_item:
        existing_item.quantity += quantity
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    flash('Product added to cart', 'success')
    return redirect(url_for('home_user'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    user_cart = Cart.query.filter_by(user_id=current_user.id).all()

    for item in user_cart:
        if item.product.units_available < item.quantity:
            flash(f'Insufficient stock for {item.product.name}', 'danger')
            return redirect(url_for('cart'))

        item.product.units_available -= item.quantity
        db.session.delete(item)

    db.session.commit()

    for item in user_cart:
        purchase = Purchase(
            product_id=item.product.id,
            category_id=item.product.category_id,
            quantity=item.quantity,
            purchase_date=datetime.utcnow()
        )
        db.session.add(purchase)

    db.session.commit()

    flash('Checkout successful', 'success')
    return redirect(url_for('cart'))


@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    products = []
    category = Category.query.filter(Category.name.ilike(f"%{query}%")).first()
    if category:
        
        products = Product.query.filter_by(category_id=category.id).all()
        if products == []:
            flash('No product in this category', 'danger')
    else:
         products = Product.query.filter(
            (Product.name.ilike(f"%{query}%")) |
            (Product.manufacturer.ilike(f"%{query}%")) |
            (Product.expiry_date.ilike(f"%{query}%"))  |
            (Product.rate_per_unit == query)
        ).all()

    return render_template('search_results.html', products=products, query=query)


@app.route('/admin/summary')
@login_required
# def admin_summary():
def admin_summary():

    purchase_data = db.session.query(Purchase.product_id, Purchase.category_id, Purchase.quantity).all()


    df = pd.DataFrame(purchase_data, columns=['product_id', 'category_id', 'quantity'])


    most_purchased_products = df.groupby('product_id')['quantity'].sum().reset_index()
  
    product_names = Product.query.with_entities(Product.id, Product.name).all()
    product_name_mapping = dict(product_names)
    most_purchased_products['product_name'] = most_purchased_products['product_id'].map(product_name_mapping)
    most_purchased_products.drop('product_id', axis='columns', inplace=True)


    plt.figure(figsize=(14, 8))
    most_purchased_products.plot(x='product_name', y='quantity', kind='bar', title='Most Purchased Products')
    plt.ylabel('Quantity Sold')
    products_graph = 'MAD1/static/most_purchased_products.png'
    filename1 = 'most_purchased_products.png'
    plt.savefig(products_graph)
    

    category_sales = df.groupby('category_id')['quantity'].sum().reset_index()
    
    category_names = Category.query.with_entities(Category.id, Category.name).all()
    category_name_mapping = dict(category_names)
    category_sales['category_name'] = category_sales['category_id'].map(category_name_mapping)
    category_sales.drop('category_id', axis='columns', inplace=True)

    plt.figure(figsize=(14, 8))
    category_sales.plot(x='category_name', y='quantity', kind='bar', title='Category-wise Sales')
    plt.ylabel('Quantity Sold')
    category_graph = 'MAD1/static/category_sales.png'
    filename2 = 'category_sales.png'
    plt.savefig(category_graph)
    
    return render_template('admin_summary.html', graph_file1=filename1, graph_file2=filename2)

