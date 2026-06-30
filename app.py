from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # This just displays our front-end page
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)