from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>School Library Management System</h1><p>Status: Under Development (Live Progress Tracking)</p>"

if __name__ == "__main__":
    app.run(debug=True)