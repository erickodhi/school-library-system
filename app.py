from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
# 🔑 Added secret key so Flask can safely display pop-up notification alerts
app.secret_key = 'super_secret_library_key'

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

class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    book_id = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.String(20), nullable=False)
    return_date = db.Column(db.String(20), nullable=True)  # Stays blank until book returns

# Recreate tables cleanly on system startup
with app.app_context():
    db.create_all()

# ==========================================
# 2. APPLICATION ROUTES (Gateways & Logic)
# ==========================================

# Gateway 1: Show the Staff Login Portal first
@app.route('/')
def login_page():
    return render_template('login.html')

# Gateway 2: Master Administration Dashboard (For ADMIN master key only)
@app.route('/dashboard')
def home():
    all_books = Book.query.all()
    all_students = Student.query.all()
    all_librarians = Librarian.query.all()
    return render_template('admin.html', books=all_books, students=all_students, librarians=all_librarians)

# Gateway 2B: Librarian Operational Desk (Fetches all issued records)
@app.route('/librarian_desk')
def librarian_desk():
    all_loans = BorrowedBook.query.all()
    return render_template('librarian.html', loans=all_loans)

# Gateway 3: Process Login Credentials with Split Traffic Controls
@app.route('/process_login', methods=['POST'])
def process_login():
    input_id = request.form.get('login_id')
    input_password = request.form.get('login_password')
    
    if input_id == "ADMIN" and input_password == "12345":
        return redirect(url_for('home')) 
        
    librarian = Librarian.query.filter_by(employee_id=input_id).first()
    if librarian and check_password_hash(librarian.password_hash, input_password):
        return redirect(url_for('librarian_desk'))
    else:
        return redirect(url_for('login_page'))

# Gateway 4: Safe Book Borrowing System (Strict Inventory Verification)
@app.route('/issue_book', methods=['POST'])
def issue_book():
    input_adm = request.form.get('student_adm')
    input_book_id = request.form.get('book_id')
    
    student_exists = Student.query.filter_by(admission_no=input_adm).first()
    book_exists = Book.query.filter_by(unique_id=input_book_id).first()
    
    # Verification Rule 1: Student must exist
    if not student_exists:
        flash('❌ Error: This Student Admission Number is not registered!', 'danger')
        return redirect(url_for('librarian_desk'))
        
    # Verification Rule 2: Book barcode must exist in the system registry
    if not book_exists:
        flash(f'❌ Error: Book ID "{input_book_id}" does not exist in the system inventory!', 'danger')
        return redirect(url_for('librarian_desk'))
    
    # Verification Rule 3: Book must not be already out
    already_borrowed = BorrowedBook.query.filter_by(book_id=input_book_id, return_date=None).first()
    if already_borrowed:
        flash('⚠ Warning: This book is currently out with another student!', 'warning')
        return redirect(url_for('librarian_desk'))

    # Success Flow: If all guards pass, lock the transaction down
    today = datetime.today().strftime('%d-%m-%Y')
    new_loan = BorrowedBook(student_id=input_adm, book_id=input_book_id, issue_date=today)
    db.session.add(new_loan)
    db.session.commit()
    
    flash(f'✅ Success: "{book_exists.title}" issued to {student_exists.name}!', 'success')
    return redirect(url_for('librarian_desk'))
    @app.route('/return_book', methods=['POST'])
def return_book():
    input_book_id = request.form.get('book_id')
    
    # Find the active loan entry where this book ID matches and has NOT been returned yet
    active_loan = BorrowedBook.query.filter_by(book_id=input_book_id, return_date=None).first()
    
    if active_loan:
        # Stamp it with today's date to close the transaction
        today = datetime.today().strftime('%d-%m-%Y')
        active_loan.return_date = today
        db.session.commit()
        
        # Get book title details to make the success message descriptive
        book_details = Book.query.filter_by(unique_id=input_book_id).first()
        title = book_details.title if book_details else "Book"
        
        flash(f'✅ Success: "{title}" has been successfully returned to shelves!', 'success')
    else:
        # If the book wasn't flagged as borrowed out in our system
        flash(f'❌ Error: Book ID "{input_book_id}" is not marked as currently borrowed out!', 'danger')
        
    return redirect(url_for('librarian_desk'))

# Gateway 5: Save a new Book
@app.route('/save_book', methods=['POST'])
def save_book():
    html_id = request.form.get('book_id_from_html')
    html_title = request.form.get('book_title_from_html')
    
    new_book = Book(unique_id=html_id, title=html_title)
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('home'))

# Gateway 6: Save a new Student
@app.route('/save_student', methods=['POST'])
def save_student():
    html_adm = request.form.get('student_adm_from_html')
    html_name = request.form.get('student_name_from_html')
    
    new_student = Student(admission_no=html_adm, name=html_name)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('home'))

# Gateway 7: Register a new Librarian
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