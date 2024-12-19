from flask import Flask, render_template, request, flash, redirect, url_for

from models import init_db, Session, Distributors, Products, Sales, Commissions, func

app = Flask(__name__)
app.config['SECRET_KEY'] = "123#ABC@123"
with app.app_context():
    init_db()


@app.route('/')
def home():
    with Session() as db_session:
        result = db_session.query(
            Distributors.distributor_name,
            func.sum(Commissions.commission)
        ).join(
            Distributors, Distributors.id == Commissions.distributor_id
        ).group_by(
            Distributors.id
        ).all()
        return render_template('index.html', result=result)


@app.route('/distributors')
def distributors():
    with Session() as db_session:
        db_distributors = db_session.query(Distributors).all()
        return render_template('distributors.html', distributors=db_distributors)


@app.route('/add_distributor', methods=['GET', 'POST'])
def add_distributor():
    with Session() as db_session:
        if request.method == 'POST':
            distributor_name = request.form['distributor_name']
            added_by_id = request.form['added_by_id']

            if not distributor_name:
                flash("Distributor name is required!", "Error")
                return redirect(url_for('add_distributor'))

            # Check if distributor already exists
            existing_distributor = db_session.query(Distributors).filter_by(distributor_name=distributor_name).first()
            if existing_distributor:
                flash(f"Distributor '{distributor_name}' already exists.", "Error")
                return redirect(url_for('add_distributor'))

            new_distributor = Distributors(distributor_name=distributor_name, added_by_id=added_by_id)
            db_session.add(new_distributor)
            try:
                db_session.commit()
                flash("New Distributor added successfully.", "Success")
            except Exception as e:
                db_session.rollback()
                flash(f"Error: {e}", "Error")
            return redirect(url_for("distributors"))
    db_distributors = db_session.query(Distributors).all()
    return render_template('add_distributor.html', distributors=db_distributors)


@app.route('/products')
def products():
    with Session() as db_session:
        db_products = db_session.query(Products).all()
        return render_template('products.html', products=db_products)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    with Session() as db_session:
        if request.method == 'POST':
            product_name = request.form['product_name']
            product_price = request.form['product_price']

            if not product_name or not product_price:
                flash("Product name and price are required!", "Error")
                return redirect(url_for('add_product'))

            new_product = Products(product_name=product_name, product_price=product_price)

            db_session.add(new_product)
            try:
                db_session.commit()
                flash("New Product added successfully.", "Success")
            except Exception as e:
                db_session.rollback()
                flash(f"Error: {e}", "Error")

            return redirect(url_for("products"))

    return render_template('add_product.html')


@app.route('/sales')
def sales():
    with Session() as db_session:
        db_sales = db_session.query(Sales).all()
        return render_template('sales.html', sales=db_sales)


@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    with Session() as db_session:
        if request.method == 'POST':
            distributor_id = request.form['distributor_id']
            product_id = request.form['product_id']

            db_distributor = db_session.get(Distributors, distributor_id)
            db_product = db_session.get(Products, product_id)

            if not db_distributor or not db_product:
                flash("Invalid distributor or product.", "Error")
                return redirect(url_for('add_sale'))

            new_sale = Sales(
                distributor_id=db_distributor.id,
                product_id=db_product.id,
                product_price=db_product.product_price,
                earned=db_product.product_price * 0.10
            )

            db_session.add(new_sale)
            try:
                db_session.commit()
            except Exception as e:
                db_session.rollback()
                flash(f"Error: {e}", "Error")
                return redirect(url_for("sales"))

            # Creating commissions chain
            current_distributor = db_distributor
            while current_distributor:
                new_commission = Commissions(sale_id=new_sale.id, distributor_id=current_distributor.id,
                                             commission=new_sale.earned)
                db_session.add(new_commission)

                current_distributor = db_session.get(Distributors, current_distributor.added_by_id)

            try:
                db_session.commit()
                flash("New Sale and commissions added successfully.", "Success")
            except Exception as e:
                db_session.rollback()
                flash(f"Error: {e}", "Error")
            return redirect(url_for("sales"))

    db_distributors = db_session.query(Distributors).all()
    db_products = db_session.query(Products).all()
    return render_template('add_sale.html', distributors=db_distributors, products=db_products)


@app.route('/commissions')
def commissions():
    with Session() as db_session:
        db_commissions = db_session.query(Commissions).all()
        return render_template('commissions.html', commissions=db_commissions)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181, debug=True)
