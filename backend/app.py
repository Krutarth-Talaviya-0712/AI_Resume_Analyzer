import os
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from extensions import db, jwt, bcrypt

load_dotenv()


def create_app():
    app = Flask(__name__)

    # CORS configuration
    allowed_origins = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": allowed_origins,
                "allow_headers": ["Content-Type", "Authorization"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            }
        },
    )

    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_url = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, 'resume_app.db')}"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # JWT configuration
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", "dev-jwt-secret-change-in-production"
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from auth.auth_routes import auth_bp
    from create_resume.resume_routes import resume_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(resume_bp, url_prefix="/api/resume")

    # API health check endpoint
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "status": "success",
            "message": "ResumeCraft API is running successfully",
            "version": "1.0.0"
        })

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        from models import User, Resume, Analysis  # noqa: F401
        db.create_all()
        print("Database tables initialized successfully.")

    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)