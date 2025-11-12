"""Flask application factory"""

import logging
from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes import health_bp, ocr_bp

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_DIR / 'ocr_service.log'),
            logging.StreamHandler()
        ]
    )

def create_app():
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize config
    Config.init_app()
    
    # Setup logging
    setup_logging()
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(ocr_bp)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("OCR Backend Service initialized")
    
    return app

__all__ = ['create_app']