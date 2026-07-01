from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  # <-- Added to automatically capture transaction dates

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fresh_library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# 1. DATABASE MODELS (Storage Tables)
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

# 🔄 NEW table to track which books are linked to which students
class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)  # Student's Admission Number
    book_id = db.Column(db.String(50), nullable=False)     # Book's Unique ID Barcode
    issue_date = db.Column(db.String(20), nullable=False)   # Date borrowed
    return_date = db.Column(db.String(20), nullable=True)   # Left empty until returned

# Recreate tables cleanly on system startup
with app.app_context():
    db.create_all()

# ==========================================
# 2. APPLICATION ROUTES (Gateways & Logic)
# ==========================================

# Gateway 1: Show the Staff Login Portal first when opening the link
@app.route('/')
def login_page():
    return render_template('login.html')

# Gateway 2: The Master Administration Dashboard (For ADMIN user only)
@app.route('/dashboard')
def home():
    all_books = Book.query.all()
    all_students = Student.query.all()
    all_librarians = Librarian.query.all()
    return render_template('admin.html', books=all_books, students=all_students, librarians=all_librarians)

# Gateway 2B: The Librarian Workstation Desk (For Staff accounts only)
@app.route('/librarian_desk')
def librarian_desk():
    return render_template('librarian.html')

# Gateway 3: Process the entered Login Credentials with Split Routing Rules
@app.route('/process_login', methods=['POST'])
def process_login():
    input_id = request.form.get('login_id')
    input_password = request.form.get('login_password')
    
    # Rule A: If Master Admin logs in -> Go to the Admin Dashboard
    if input_id == "ADMIN" and input_password == "12345":
        return redirect(url_for('home')) 
        
    # Rule B: If a standard Librarian logs in -> Go to the Librarian Desk
    librarian = Librarian.query.filter_by(employee_id=input_id).first()
    if librarian and check_password_hash(librarian.password_hash, input_password):
        return redirect(url_for('librarian_desk'))
    else:
        return redirect(url_for('login_page'))

# 🔄 NEW Gateway: Processes the book issue transaction from the Librarian page
@app.route('/issue_book', methods=['POST'])
def issue_book():
    input_adm = request.form.get('student_adm')
    input_book_id = request.form.get('book_id')
    
    # Verify if the student and book actually exist in our database inventory
    student_exists = Student.query.filter_by(admission_no=input_adm).first()
    book_exists = Book.query.filter_by(unique_id=input_book_id).first()
    
    if student_exists and book_exists:
        today = datetime.today().strftime('%d-%m-%Y') # Captures active date
        
        # Save transaction entry
        new_loan = BorrowedBook(student_id=input_adm, book_id=input_book_id, issue_date=today)
        db.session.add(new_loan)
        db.session.commit()
        
    return redirect(url_for('librarian_desk'))

# Gateway 4: Save a new Book to the database
@app.route('/save_book', methods=['POST'])
def save_book():
    html_id = request.form.get('book_id_from_html')
    html_title = request.form.get('book_title_from_html')
    
    new_book = Book(unique_id=html_id, title=html_title)
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('home'))

# Gateway 5: Save a new Student to the database
@app.route('/save_student', methods=['POST'])
def save_student():
    html_adm = request.form.get('student_adm_from_html')
    html_name = request.form.get('student_name_from_html')
    
    new_student = Student(admission_no=html_adm, name=html_name)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('home'))

# Gateway 6: Register a new Librarian (With password hashing)
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