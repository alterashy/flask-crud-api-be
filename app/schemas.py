from marshmallow import Schema, fields, validate

class UserRegisterSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    gender = fields.String(validate=validate.OneOf(["male", "female", "other", "prefer_not_to_say"]))
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)

class UserPublicSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    email = fields.Email()
    gender = fields.String(allow_none=True)
    created_at = fields.DateTime()

class ProductCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()
    price = fields.Decimal(as_string=True)

class ProductOutSchema(ProductCreateSchema):
    id = fields.Integer()
    owner_id = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()