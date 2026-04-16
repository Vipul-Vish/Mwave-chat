from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from models import db, User
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mwave_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

socketio = SocketIO(app, cors_allowed_origins="*")

# Register Blueprints
from routes import routes
app.register_blueprint(routes)

# Register Sockets
import sockets
sockets.register_socket_events(socketio)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)