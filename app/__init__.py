from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app(config_filename=None):
    config_filename = config_filename or '../instance/config.py'

    app = Flask(__name__)

    app.config.from_pyfile(config_filename)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)
    bcrypt.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'login.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'danger'


    from app.routes.dashboard.dashboard import dashboard_bp
    from app.routes.grid.grid import grid_bp
    from app.routes.reports.reports import reports_bp
    from app.routes.crud.crud import crud_bp
    from app.routes.login.login import login_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(grid_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(crud_bp)
    app.register_blueprint(login_bp)

    return app


create_app()
