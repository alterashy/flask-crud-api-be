from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import asc, desc
from .extensions import db
from .models import Product
from .schemas import ProductCreateSchema, ProductOutSchema

product_bp = Blueprint("products", __name__)
create_schema = ProductCreateSchema()
out_schema = ProductOutSchema()

def parse_sort(qs, default="-created_at"):
    sort = qs.get("sort", default)
    direction = desc if sort.startswith("-") else asc
    field = sort.lstrip("-")
    return direction(getattr(Product, field, Product.created_at))

@product_bp.post("")
@jwt_required()
def create_product():
    """
    Create a new product
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
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
            - price
          properties:
            name:
              type: string
              example: Mechanical Keyboard
            price:
              type: number
              example: 499000
            description:
              type: string
              example: RGB backlit
    responses:
      201:
        description: Product created
    """
    data = create_schema.load(request.get_json() or {})
    owner_id = int(get_jwt_identity())
    product = Product(owner_id=owner_id, **data)
    db.session.add(product)
    db.session.commit()
    return {
        "status": "success",
        "code": 201,
        "message": "Product created",
        "data": out_schema.dump(product)
    }, 201

@product_bp.get("")
@jwt_required()
def list_products():
    """
    Get list of products
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
      - name: sort
        in: query
        type: string
        required: false
        default: -created_at
    """
    owner_id = int(get_jwt_identity())
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(int(request.args.get("per_page", 10)), 100)
    q = Product.query.filter_by(owner_id=owner_id)
    q = q.order_by(parse_sort(request.args))
    items = q.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "status": "success",
        "code": 200,
        "message": "Products fetched",
        "data": {
            "items": [out_schema.dump(i) for i in items.items],
            "page": items.page,
            "pages": items.pages,
            "total": items.total
        }
    }, 200

@product_bp.get("/<int:product_id>")
@jwt_required()
def get_product(product_id):
    """
    Get product detail
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID of the product
    """
    owner_id = int(get_jwt_identity())
    product = Product.query.filter_by(id=product_id, owner_id=owner_id).first()
    if not product:
        return {"message": "Not found"}, 404
    return out_schema.dump(product)

@product_bp.put("/<int:product_id>")
@jwt_required()
def update_product(product_id):
    """
    Update product
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    consumes:
      - application/json
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Gaming Mouse
            price:
              type: number
              example: 459000
            description:
              type: string
              example: Wireless RGB mouse
    """
    owner_id = int(get_jwt_identity())
    product = Product.query.filter_by(id=product_id, owner_id=owner_id).first()
    if not product:
        return {
            "status": "error",
            "code": 404,
            "message": "Not found",
            "data": None
        }, 404

    data = create_schema.load(request.get_json() or {}, partial=True)
    for k, v in data.items():
        setattr(product, k, v)
    db.session.commit()
    return {
        "status": "success",
        "code": 200,
        "message": "Product updated",
        "data": out_schema.dump(product)
    }, 200

@product_bp.delete("/<int:product_id>")
@jwt_required()
def delete_product(product_id):
    """
    Delete product
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        
    """
    owner_id = int(get_jwt_identity())
    product = Product.query.filter_by(id=product_id, owner_id=owner_id).first()
    if not product:
        return {
            "status": "error",
            "code": 404,
            "message": "Not found",
            "data": None
        }, 404

    db.session.delete(product)
    db.session.commit()
    return {
        "status": "success",
        "code": 200,
        "message": "Product deleted",
        "data": None
    }, 200
