import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from .config import Config
from .extensions import db, migrate, jwt
from .auth_routes import auth_bp
from .product_routes import product_bp
from .profile_routes import profile_bp

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Flask Simple API",
        "description": "Auth + Profile + Product CRUD",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "bearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ],
}

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    Swagger(app, template=swagger_template)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(profile_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        """
        Health check
        ---
        responses:
            200:
                description: API is healthy
        examples:
            application/json: {"status": "ok"}
        """
        return {"status": "ok"}

    return app