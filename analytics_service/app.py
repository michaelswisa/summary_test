from flask import Flask
from analytics_service.routes.map_routes import map_bp
from analytics_service.routes.region_change_routes import region_change_bp

app = Flask(__name__, template_folder='templates')

app.register_blueprint(map_bp)
app.register_blueprint(region_change_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
