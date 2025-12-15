from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "corporate_secret_key"

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- DATABASE MODELS ---------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    theme = db.Column(db.String(10), default="light")

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acc_no = db.Column(db.String(20))
    acc_type = db.Column(db.String(30))
    balance = db.Column(db.Float)
    user_id = db.Column(db.Integer)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    description = db.Column(db.String(100))
    amount = db.Column(db.Float)
    user_id = db.Column(db.Integer)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_type = db.Column(db.String(50))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20))
    user_id = db.Column(db.Integer)

# ---------------- ROUTES ---------------- #

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    return "Invalid Login"

@app.route('/dashboard')
def dashboard():
    uid = session.get('user_id')
    accounts = Account.query.filter_by(user_id=uid).count()
    transactions = Transaction.query.filter_by(user_id=uid).count()
    loans = Loan.query.filter_by(user_id=uid).count()
    return render_template('dashboard.html',
                           acc_count=accounts,
                           txn_count=transactions,
                           loan_count=loans)

@app.route('/accounts')
def accounts():
    uid = session.get('user_id')
    data = Account.query.filter_by(user_id=uid).all()
    return render_template('accounts.html', accounts=data)

@app.route('/transactions')
def transactions():
    uid = session.get('user_id')
    data = Transaction.query.filter_by(user_id=uid).all()
    return render_template('transactions.html', transactions=data)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    uid = session.get('user_id')
    if request.method == 'POST':
        acc = request.form['acc_no']
        amt = float(request.form['amount'])
        txn = Transaction(
            date="Today",
            description=f"Transfer to {acc}",
            amount=-amt,
            user_id=uid
        )
        db.session.add(txn)
        db.session.commit()
        return redirect(url_for('transactions'))
    return render_template('transfer.html')

@app.route('/loans')
def loans():
    uid = session.get('user_id')
    data = Loan.query.filter_by(user_id=uid).all()
    return render_template('loans.html', loans=data)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    uid = session.get('user_id')
    user = User.query.get(uid)
    if request.method == 'POST':
        user.email = request.form['email']
        user.phone = request.form['phone']
        db.session.commit()
    return render_template('profile.html', user=user)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    uid = session.get('user_id')
    user = User.query.get(uid)
    if request.method == 'POST':
        user.theme = request.form['theme']
        db.session.commit()
    return render_template('settings.html', theme=user.theme)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
