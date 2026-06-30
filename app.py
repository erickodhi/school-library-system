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
    all_students = Student.query.all()  # <-- Add this line
    
    # Update this line to pass 'students' as well:
    return render_template('admin.html', books=all_books, students=all_students)
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

if __name__ == '__main__':
    app.run(debug=True)