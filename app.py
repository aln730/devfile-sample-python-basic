from flask import Flask, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

def create_admin():
    if not User.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
        admin = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the home page'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        return jsonify({'message': 'Login successful!', 'success': True})
    return jsonify({'message': 'Invalid credentials!', 'success': False})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = generate_password_hash(data.get('password'), method='pbkdf2:sha256')
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists!', 'success': False})
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Account created!', 'success': True})

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return jsonify({'message': 'Please login first!', 'success': False})
    return jsonify({'message': 'Welcome to your dashboard', 'is_admin': session.get('is_admin', False)})

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully!', 'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
