from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
# 🔑 Secret key for notification alerts
app.secret_key = 'super_secret_library_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fresh_library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==========================================
# 1. DATABASE MODELS (Storage Tables)
# ==========================================

# 👑 Master Catalog managed ONLY by the Super Admin
class MasterCatalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False) # e.g., "Secondary Mathematics Form 3"

# 🏫 Physical inventory managed by the Admin (Title selected from dropdown)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), unique=True, nullable=False) # Barcode typed by Admin
    title = db.Column(db.String(150), nullable=False) # Selected from Super Admin's catalog

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)

class Librarian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    book_id = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.String(20), nullable=False)
    return_date = db.Column(db.String(20), nullable=True)

# Recreate tables cleanly on system startup
with app.app_context():
    db.create_all()

# ==========================================
# 2. APPLICATION ROUTES (Gateways & Logic)
# ==========================================

# Gateway 1: Staff Login Portal
@app.route('/')
def login_page():
    return render_template('login.html')

# 👑 Gateway 1B: Super Administration Dashboard (Manages Master Catalog Titles)
@app.route('/super_admin')
def super_admin_dashboard():
    catalog_items = MasterCatalog.query.all()
    total_titles = len(catalog_items)
    return render_template('super_admin.html', catalog=catalog_items, total_titles=total_titles)

# Gateway 2: Master Administration Dashboard (Loads the MasterCatalog for dropdown selection)
@app.route('/dashboard')
def home():
    all_books = Book.query.all()
    all_students = Student.query.all()
    all_librarians = Librarian.query.all()
    master_catalog = MasterCatalog.query.all() # Passed so Admin can pick from it
    return render_template('admin.html', books=all_books, students=all_students, librarians=all_librarians, master_catalog=master_catalog)

# Gateway 2B: Librarian Operational Desk Workspace
@app.route('/librarian_desk')
def librarian_desk():
    all_loans = BorrowedBook.query.all()
    all_books = Book.query.all()       
    all_students = Student.query.all() 
    return render_template('librarian.html', loans=all_loans, books=all_books, students=all_students)

# Gateway 3: Split Login Routing Engine
@app.route('/process_login', methods=['POST'])
def process_login():
    input_id = request.form.get('login_id')
    input_password = request.form.get('login_password')
    
    # 👑 Login Rule A: Super Admin
    if input_id == "SUPER_ADMIN" and input_password == "master99":
        return redirect(url_for('super_admin_dashboard'))
        
    # 🏫 Login Rule B: Standard Admin
    if input_id == "ADMIN" and input_password == "12345":
        return redirect(url_for('home')) 
        
    # 📖 Login Rule C: Librarian
    librarian = Librarian.query.filter_by(employee_id=input_id).first()
    if librarian and check_password_hash(librarian.password_hash, input_password):
        return redirect(url_for('librarian_desk'))
    else:
        return redirect(url_for('login_page'))

# 👑 Action Route: Save Master Book Title from Super Admin Page
@app.route('/save_master_title', methods=['POST'])
def save_master_title():
    new_title = request.form.get('master_title').strip()
    exists = MasterCatalog.query.filter_by(title=new_title).first()
    
    if not exists and new_title:
        db.session.add(MasterCatalog(title=new_title))
        db.session.commit()
        flash(f'✅ Catalog Updated: "{new_title}" added successfully!', 'success')
    else:
        flash('⚠ Warning: This title already exists in the catalog.', 'warning')
        
    return redirect(url_for('super_admin_dashboard'))

# Action Route: Save a Physical Book Copy (Title comes from the dropdown)
@app.route('/save_book', methods=['POST'])
def save_book():
    html_title = request.form.get('book_title_from_html') # From dropdown selection
    html_id = request.form.get('book_id_from_html')       # From manual input/scanner
    
    new_book = Book(unique_id=html_id, title=html_title)
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('home'))

# Action Route: Issue Book Engine
@app.route('/issue_book', methods=['POST'])
def issue_book():
    input_adm = request.form.get('student_adm')
    input_book_id = request.form.get('book_id')
    
    student_exists = Student.query.filter_by(admission_no=input_adm).first()
    book_exists = Book.query.filter_by(unique_id=input_book_id).first()
    
    if not student_exists:
        flash('❌ Error: This Student Admission Number is not registered!', 'danger')
        return redirect(url_for('librarian_desk'))
        
    if not book_exists:
        flash(f'❌ Error: Book ID "{input_book_id}" does not exist in the system inventory!', 'danger')
        return redirect(url_for('librarian_desk'))
    
    already_borrowed = BorrowedBook.query.filter_by(book_id=input_book_id, return_date=None).first()
    if already_borrowed:
        flash('⚠ Warning: This book is currently out with another student!', 'warning')
        return redirect(url_for('librarian_desk'))

    today = datetime.today().strftime('%d-%m-%Y')
    new_loan = BorrowedBook(student_id=input_adm, book_id=input_book_id, issue_date=today)
    db.session.add(new_loan)
    db.session.commit()
    
    flash(f'✅ Success: "{book_exists.title}" issued to {student_exists.name}!', 'success')
    return redirect(url_for('librarian_desk'))

# Action Route: Return Book Engine
@app.route('/return_book', methods=['POST'])
def return_book():
    input_book_id = request.form.get('book_id')
    active_loan = BorrowedBook.query.filter_by(book_id=input_book_id, return_date=None).first()
    
    if active_loan:
        today = datetime.today().strftime('%d-%m-%Y')
        active_loan.return_date = today
        db.session.commit()
        book_details = Book.query.filter_by(unique_id=input_book_id).first()
        title = book_details.title if book_details else "Book"
        flash(f'✅ Success: "{title}" has been successfully returned to shelves!', 'success')
    else:
        flash(f'❌ Error: Book ID "{input_book_id}" is not marked as currently borrowed out!', 'danger')
        
    return redirect(url_for('librarian_desk'))

# Action Route: Save a new Student
@app.route('/save_student', methods=['POST'])
def save_student():
    html_adm = request.form.get('student_adm_from_html')
    html_name = request.form.get('student_name_from_html')
    new_student = Student(admission_no=html_adm, name=html_name)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('home'))

# Action Route: Register a new Librarian
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