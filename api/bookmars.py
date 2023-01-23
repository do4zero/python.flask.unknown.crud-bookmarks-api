from flask import Blueprint, request, jsonify
from api.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from api.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity, jwt_required

import validators

bookmarks = Blueprint("bookmarks",__name__,url_prefix="/api/v1/bookmarks")

@bookmarks.route('/', methods=['POST','GET'])
@jwt_required()
def bookmarks_index():
    current_user = get_jwt_identity()
    
    if request.method == 'POST':
        body = request.get_json().get('body','')
        url = request.get_json().get('url','')
        
        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST 
        
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists',
            }), HTTP_409_CONFLICT
        
        bookmark = Bookmark(url=url, body=body, user_id=current_user)

        db.session.add(bookmark)
        db.session.commit()
        
        return jsonify({
            'id': bookmark.id,
            'body': bookmark.body,
            'url': bookmark.url,
            'short_url':bookmark.short_url,
            'visits': bookmark.visits,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }), HTTP_201_CREATED
        
    else:
        page = request.args.get('page',1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        
        bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
        
        data = [
            {
                'id': bookmark.id,
                'body': bookmark.body,
                'url': bookmark.url,
                'short_url':bookmark.short_url,
                'visit': bookmark.visits,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at
            } 
            for bookmark in bookmarks
        ]
        
        meta = {
            "page": bookmarks.page,
            "pages":bookmarks.pages,
            "total_count":bookmarks.total,
            "prev": bookmarks. prev_num,
            "next": bookmarks.next_num,
            "has_prev": bookmarks.has_prev,
            "has_next": bookmarks.has_next,
        }
        
        return jsonify({'data': data, 'meta': meta}), HTTP_200_OK

@bookmarks.get("/<int:id>")
@jwt_required()
def bookmarks_detail(id):
    current_user = get_jwt_identity()
    
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    
    if not bookmark:
        return jsonify({
            'message': 'Item not found'
        }), HTTP_404_NOT_FOUND
    
    return jsonify({
            'id': bookmark.id,
            'body': bookmark.body,
            'url': bookmark.url,
            'short_url':bookmark.short_url,
            'visits': bookmark.visits,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }), HTTP_200_OK

@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()

def bookmarsk_edit(id):
    current_user = get_jwt_identity()
    
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    
    if not bookmark:
        return jsonify({
            'message': 'Item not found'
        }), HTTP_404_NOT_FOUND
    
    body = request.get_json().get('body','')
    url = request.get_json().get('url','')
    
    if not validators.url(url):
        return jsonify({
            'error': 'Enter a valid url'
        }), HTTP_400_BAD_REQUEST
    
    bookmark.url = url
    bookmark.body = body
    
    db.session.commit()
        
    return jsonify({
        'id': bookmark.id,
        'body': bookmark.body,
        'url': bookmark.url,
        'short_url':bookmark.short_url,
        'visits': bookmark.visits,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
    }), HTTP_200_OK
    
    
@bookmarks.delete("/<int:id>")
@jwt_required()
def bookmarks_delete(id):
    current_user = get_jwt_identity()
    
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    
    if not bookmark:
        return jsonify({
            'message': 'Item not found'
        }), HTTP_404_NOT_FOUND
    
    db.session.delete(bookmark)
    db.session.commit()
    
    return jsonify({}), HTTP_204_NO_CONTENT