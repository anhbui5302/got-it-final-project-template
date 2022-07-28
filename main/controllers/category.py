from main import app, db
from main.commons.decorators import (
    authentication,
    validate_request_args,
    validate_request_body,
)
from main.commons.exceptions import Forbidden, NotFound, ValueExistedError
from main.models.category import CategoryModel
from main.schemas.base import PaginationSchema
from main.schemas.category import CategorySchema


@app.route("/categories", methods=["GET"])
@validate_request_args(schema_class=PaginationSchema)
@authentication(optional=True)
def get_all_categories(**kwargs):
    user_id = kwargs.get("user_id")  # id of logged-in user, None if guest.

    args = kwargs.get("query_args")
    page, per_page = args.values()
    start_id = (page - 1) * per_page
    end_id = page * per_page

    categories_schema = CategorySchema(many=True)
    categories_schema.context["authenticated_user_id"] = user_id
    categories = CategoryModel.get_multiple(start_id, end_id)

    result = {"categories": categories_schema.dump(categories)}
    total = CategoryModel.get_count()
    pagination_result = {"page": page, "per_page": per_page, "total": total}
    return {**result, **pagination_result}


@app.route("/categories", methods=["POST"])
@validate_request_body(schema_class=CategorySchema)
@authentication()
def create_category(**kwargs):
    user_id = kwargs.get("user_id")  # id of logged-in user, None if guest.

    data = kwargs["data"]
    # Check if another category with the same name exists in the database.
    if CategoryModel.get_by_name(data["name"]):
        raise ValueExistedError(error_data={"name": ["Name already exists."]})

    # Create new category and add to database.
    category = CategoryModel(user_id, data["name"])
    db.session.add(category)
    db.session.commit()

    category_schema = CategorySchema()
    category_schema.context["authenticated_user_id"] = user_id
    return category_schema.dump(category)


@app.route("/categories/<int:category_id>", methods=["DELETE"])
@authentication()
def delete_category(category_id, **kwargs):
    user_id = kwargs.get("user_id")  # id of logged-in user, None if guest.

    # Check if the category exists in the database
    category = CategoryModel.get_by_id(category_id)
    if not category:
        raise NotFound(error_message="The specified category does not exist.")
    elif category.user_id != user_id:
        raise Forbidden(error_message="User does not have sufficient permissions.")
    else:
        # Delete all items in the category from db
        db.session.delete(category)

    db.session.commit()
    return {}
