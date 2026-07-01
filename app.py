from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fresh_library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# 1. DATABASE MODELS (Tables)
# ==========================================

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)

class Librarian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Recreate tables cleanly on startup
with app.app_context():
    db.create_all()

# ==========================================
# 2. APPLICATION ROUTES
# ==========================================
@app.route('/')
def login_page():
    return render_template('login.html')
    # Gateway 3: Process the entered Login Credentials
@app.route('/process_login', methods=['POST'])
def process_login():
    input_id = request.form.get('login_id')
    input_password = request.form.get('login_password')
    
    # 🔑 NEW: THE MASTER KEY BYPASS
    if input_id == "ADMIN" and input_password == "12345":
        return redirect(url_for('home')) # Let them straight into the dashboard
        
    # Standard database check (for librarians you register later)
    librarian = Librarian.query.filter_by(employee_id=input_id).first()
    if librarian and check_password_hash(librarian.password_hash, input_password):
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login_page'))
@app.route('/dashboard')
def home():
    all_books = Book.query.all()
    all_students = Student.query.all()
    all_librarians = Librarian.query.all()
    return render_template('admin.html', books=all_books, students=all_students, librarians=all_librarians)

@app.route('/save_book', methods=['POST'])
def save_book():
    html_id = request.form.get('book_id_from_html')
    html_title = request.form.get('book_title_from_html')
    
    new_book = Book(unique_id=html_id, title=html_title)
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/save_student', methods=['POST'])
def save_student():
    html_adm = request.form.get('student_adm_from_html')
    html_name = request.form.get('student_name_from_html')
    
    new_student = Student(admission_no=html_adm, name=html_name)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/save_librarian', methods=['POST'])
def save_librarian():
    html_emp_id = request.form.get('lib_id_from_html')
    html_name = request.form.get('lib_name_from_html')
    html_password = request.form.get('lib_password_from_html')
    
    secure_password = generate_password_hash(html_password)
    
    new_librarian = Librarian(employee_id=html_emp_id, name=html_name, password_hash=secure_password)
    db.session.add(new_librarian)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)