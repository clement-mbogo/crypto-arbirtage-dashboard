from flask import Flask, render_template
from flask_cors import CORS
from api import api_blueprint
from scheduler import start_scheduler

app = Flask(__name__)
CORS(app)

# Register API routes from api.py
app.register_blueprint(api_blueprint, url_prefix='/api')

# Route to frontend dashboard
@app.route('/')
def index():
    return render_template('index.html')

# Start price fetching scheduler
start_scheduler()

if __name__ == '__main__':
    app.run(debug=True, port=10000)
