from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # render_template searches inside your 'templates' folder automatically
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)