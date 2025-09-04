from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
from .schemas import UserPublicSchema

profile_bp = Blueprint("profile", __name__)
user_public = UserPublicSchema()

@profile_bp.get("/me")
@jwt_required()
def me():
    """
    Get current user profile
    ---
    tags:
      - Profile
    security:
      - bearerAuth: []
    responses:
      200:
        description: current user profile
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            code:
              type: integer
              example: 200
            message:
              type: string
              example: Profile fetched
            data:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                email:
                  type: string
      401:
        description: Missing or invalid JWT
        schema:
          type: object
          properties:
            msg:
              type: string
              example: Missing Authorization Header
    """
    uid = get_jwt_identity()
    user = User.query.get(int(uid))
    if not user:
        return {
            "status": "error",
            "code": 404,
            "message": "User not found",
            "data": None
        }, 404

    return {
        "status": "success",
        "code": 200,
        "message": "Profile fetched",
        "data": user_public.dump(user)
    }, 200