from flask import Flask, redirect, jsonify
import os
from api.auth import auth
from api.bookmars import bookmarks
from api.database import db, Bookmark
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from api.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=str(os.environ.get("JWT_SECRET_KEY"))    
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    JWTManager(app)
    
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    CORS(app)
    
    @app.get('/<short_url>')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()
        
        if bookmark:
            bookmark.visits = bookmark.visits + 1
            db.session.commit()
            
            return redirect(bookmark.url)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error':'Not found'}), HTTP_404_NOT_FOUND
    
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error':'Oops something went wrong, we are working on it.'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    return app
