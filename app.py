from flask import Flask
from route import route_bp

app = Flask(__name__)

app.register_blueprint(route_bp)

if __name__ == '__main__':
    app.run(debug=True)
