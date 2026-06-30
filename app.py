from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fresh_library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 1. OUR DATABASE MODEL (Storage)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)

# 2. OUR ROUTE TO SHOW THE PAGE (Front End Router)
@app.route('/')
def home():
    return render_template('admin.html')

# 3. OUR ROUTE TO SAVE THE DATA (The Engine)
@app.route('/save_book', methods=['POST'])
def save_book():
    # Grab what the user typed in the HTML boxes
    html_id = request.form.get('book_id_from_html')
    html_title = request.form.get('book_title_from_html')
    
    # Package it into our Database layout
    new_book = Book(unique_id=html_id, title=html_title)
    
    # Save it permanently to fresh_library.db
    db.session.add(new_book)
    db.session.commit()
    
    return "Success! Book has been saved to the database. Press back to add another."

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates the database file instantly
    app.run(debug=True)