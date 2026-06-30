from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'library_clean_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =======================================================
# DATABASE MODELS
# =======================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Admin' or 'Librarian'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(20), nullable=False) 

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_book_id = db.Column(db.String(50), unique=True, nullable=False) 
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='Available') 

# =======================================================
# ROUTES & WORKSPACE
# =======================================================

@app.route('/')
def admin_panel():
    return render_template('admin.html')

@app.route('/add_librarian', methods=['POST'])
def add_librarian():
    username = request.form.get('username')
    password = request.form.get('password')
    new_user = User(username=username, password=password, role='Librarian')
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/add_student', methods=['POST'])
def add_student():
    admission_no = request.form.get('admission_no')
    name = request.form.get('name')
    grade = request.form.get('grade')
    new_student = Student(admission_no=admission_no, name=name, grade=grade)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/add_book', methods=['POST'])
def add_book():
    unique_id = request.form.get('unique_book_id')
    title = request.form.get('title')
    author = request.form.get('author')
    new_book = Book(unique_book_id=unique_id, title=title, author=author)
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)