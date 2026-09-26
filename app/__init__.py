from flask import Flask
from flask_cors import CORS
from mysql.connector import connect, Error
import os

def _ssl_args():
    """Cloud databases (e.g. TiDB Cloud) require an encrypted connection.
    Set MYSQL_SSL_CA to a CA bundle path to enable it; leave unset for local MySQL."""
    ca = os.getenv("MYSQL_SSL_CA")
    if not ca:
        return {}
    return {"ssl_ca": ca, "ssl_verify_cert": True, "ssl_verify_identity": True}

def get_mysql_connection():
    """Create and return a MySQL connection."""
    try:
        connection = connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),  
            port=int(os.getenv("MYSQL_PORT", 3306)),    
            user=os.getenv("MYSQL_USER", "root"),      
            password=os.getenv("MYSQL_PASSWORD", "root"),  
            database=os.getenv("MYSQL_DATABASE", "user"),
            **_ssl_args(),
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    # Allow requests from your frontend. Set FRONTEND_URL on the host (comma-separated for several).
    CORS(app, origins=os.getenv("FRONTEND_URL", "*").split(","))

    # Configuration
    app.config.from_object('config.Config')

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.program import program_bp

    # app.register_blueprint(auth_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(program_bp)

    @app.route("/")
    def health():
        return {"status": "ok"}

    return app
