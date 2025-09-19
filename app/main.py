from flask import Flask, jsonify, request, render_template
import os
from dotenv import load_dotenv
from app.admin_routes import admin_bp

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


app.register_blueprint(admin_bp)

@app.route('/')
def home():
    return jsonify({"message": "PrePair Central API is running!"})

@app.route('/api/activate', methods=['POST'])
def activate():
    data = request.get_json()
    return jsonify({"status": "success", "message": "Mock activation successful"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
