from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from .extensions import db
from .models import User
from .schemas import UserRegisterSchema, UserLoginSchema, UserPublicSchema

auth_bp = Blueprint("auth", __name__)

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()
user_public = UserPublicSchema()

@auth_bp.post("/register")
def register():
    """
    Register a new user
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: john doe
            email:
              type: string
              example: john@mail.com
            password:
              type: string
              example: secret
            gender:
              type: string
              example: female
    responses:
      201:
        description: User created
    """

    data = register_schema.load(request.get_json() or {})
    if User.query.filter_by(email=data["email"]).first():
        return {
            "status": "error",
            "code": 409,
            "message": "Email already exists",
            "data": None
        }, 409

    user = User(
        name=data["name"],
        email=data["email"],
        gender=data.get("gender"),
        password_hash=User.hash_password(data["password"]),
    )
    db.session.add(user)
    db.session.commit()
    return {
        "status": "success",
        "code": 201,
        "message": "User registered",
        "data": user_public.dump(user)
    }, 201

@auth_bp.post("/login")
def login():
    """
    User login
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: john@mail.com
            password:
              type: string
              example: secretpass
    responses:
      200:
        description: Login successful (returns tokens)
    """

    data = login_schema.load(request.get_json() or {})
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.verify_password(data["password"]):
        return {
            "status": "error",
            "code": 401,
            "message": "Invalid credentials",
            "data": None
        }, 401

    identity = str(user.id)
    tokens = {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
    }
    return {
        "status": "success",
        "code": 200,
        "message": "Login successful",
        "data": tokens
    }, 200

@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    responses:
      200:
        description: New access token
    """
    uid = get_jwt_identity()
    access = create_access_token(identity=uid)
    return {"access_token": access}