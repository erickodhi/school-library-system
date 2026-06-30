# 2. UPDATED ROUTE TO SHOW THE PAGE + THE LIST OF BOOKS
@app.route('/')
def home():
    # Fetch all books currently saved in our database table
    all_books_in_db = Book.query.all()
    # Pass that list over to the HTML file using a variable named 'books'
    return render_template('admin.html', books=all_books_in_db)

# 3. UPDATED ROUTE TO SAVE AND REDIRECT HOME (Fixes the blank page!)
@app.route('/save_book', methods=['POST'])
def save_book():
    html_id = request.form.get('book_id_from_html')
    html_title = request.form.get('book_title_from_html')
    
    new_book = Book(unique_id=html_id, title=html_title)
    db.session.add(new_book)
    db.session.commit()
    
    # Instead of a blank screen, refresh and send the user back to the home page!
    return redirect(url_for('home'))