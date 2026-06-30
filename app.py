from flask import Flask, render_template

app = Flask(__name__)

# This explicitly maps the main domain link "/" to our admin page
@app.route('/')
def home():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)