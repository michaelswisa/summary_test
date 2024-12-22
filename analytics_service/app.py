from flask import Flask
from analytics_service.routes.attack_type_routes import attack_type_bp

app = Flask(__name__)

app.register_blueprint(attack_type_bp)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
