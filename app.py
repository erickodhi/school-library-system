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

# ====== MOVED OUTSIDE THE MAIN BLOCK FOR RENDER/GUNICORN ======
with app.app_context():
    db.create_all() # This forces Render to create the tables on startup!
# ==============================================================

# 2. ROUTE TO SHOW THE PAGE + THE LIST OF BOOKS
@app.route('/')
def home():
    all_books_in_db = Book.query.all()
    return render_template('admin.html', books=all_books_in_db)

# 3. ROUTE TO SAVE AND REDIRECT HOME
@app.route('/save_book', methods=['POST'])
def save_book():
    html_id = request.form.get('book_id_from_html')
    html_title = request.form.get('book_title_from_html')
    
    new_book = Book(unique_id=html_id, title=html_title)
    db.session.add(new_book)
    db.session.commit()
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)