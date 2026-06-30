from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fresh_library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 1. OUR DATABASE MODEL
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    # --------------------
    # ======= PASTE THIS RIGHT BELOW CLASS BOOK =======
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
# ================================================

# ====== MOVED OUTSIDE THE MAIN BLOCK FOR RENDER/GUNICORN ======
with app.app_context():
    db.create_all() # This forces Render to create the tables on startup!
# ==============================================================

# 2. ROUTE TO SHOW THE PAGE + THE LIST OF BOOKS
# ======= REPLACE YOUR HOME ROUTE WITH THIS =======
@app.route('/')
def home():
    all_books = Book.query.all()
    all_students = Student.query.all()
    all_librarians = Librarian.query.all() # <-- Add this line
    
    # Update the return statement to include librarians:
    return render_template('admin.html', books=all_books, students=all_students, librarians=all_librarians)
# ==================================================

# 3. ROUTE TO SAVE AND REDIRECT HOME
@app.route('/save_book', methods=['POST'])
def save_book():
    html_id = request.form.get('book_id_from_html')
    html_title = request.form.get('book_title_from_html')
    
    new_book = Book(unique_id=html_id, title=html_title)
    db.session.add(new_book)
    db.session.commit()
    
    return redirect(url_for('home'))
    # ======= PASTE THIS BELOW YOUR SAVE_BOOK ROUTE =======
@app.route('/save_student', methods=['POST'])
def save_student():
    html_adm = request.form.get('student_adm_from_html')
    html_name = request.form.get('student_name_from_html')
    
    new_student = Student(admission_no=html_adm, name=html_name)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('home'))
# ====================================================
class Librarian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    @app.route('/save_librarian', methods=['POST'])
def save_librarian():
    html_emp_id = request.form.get('lib_id_from_html')
    html_name = request.form.get('lib_name_from_html')
    html_password = request.form.get('lib_password_from_html')
    
    # Securely scramble the password before saving
    secure_password = generate_password_hash(html_password)
    
    new_librarian = Librarian(employee_id=html_emp_id, name=html_name, password_hash=secure_password)
    db.session.add(new_librarian)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)