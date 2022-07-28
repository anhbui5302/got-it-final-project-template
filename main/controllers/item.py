from main import app, db
from main.commons.decorators import (
    authentication,
    validate_request_args,
    validate_request_body,
)
from main.commons.exceptions import Forbidden, NotFound, ValueExistedError
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.schemas.base import ItemPaginationSchema
from main.schemas.item import ItemSchema


@app.route("/items", methods=["GET"])
@validate_request_args(schema_class=ItemPaginationSchema)
@authentication(optional=True)
def get_all_items(**kwargs):
    user_id = kwargs.get("user_id")  # id of logged-in user, None if guest.

    args = kwargs.get("query_args")
    page, per_page, category_id = args.values()
    start_id = (page - 1) * per_page
    end_id = page * per_page

    items_schema = ItemSchema(many=True)
    items_schema.context["authenticated_user_id"] = user_id
    # Get items
    if not category_id:
        items = ItemModel.get_multiple(start_id, end_id)
        total = ItemModel.get_count()
    else:
        if not CategoryModel.get_by_id(category_id):
            raise NotFound(error_message="The specified category does not exist.")

        items = ItemModel.get_multiple(start_id, end_id, category_id)
        total = ItemModel.get_count(category_id)

    pagination_result = {"page": page, "per_page": per_page, "total": total}
    result = {"items": items_schema.dump(items)}
    return {**result, **pagination_result}


@app.route("/items/<int:item_id>", methods=["GET"])
@authentication(optional=True)
def get_item(item_id, **kwargs):
    user_id = kwargs.get("user_id")  # id of logged-in user, None if guest.

    # Check if the item exists in the database
    item = ItemModel.get_by_id(item_id)
    if not item:
        raise NotFound(error_message="The specified item does not exist.")

    item_schema = ItemSchema()
    item_schema.context["authenticated_user_id"] = user_id
    result = item_schema.dump(item)

    return result


@app.route("/items", methods=["POST"])
@validate_request_body(schema_class=ItemSchema)
@authentication()
def create_item(**kwargs):
    user_id = kwargs.get("user_id")  # id of logged-in user, None if guest.

    data = kwargs["data"]

    # Check if the category_id specified exists in the database
    if not CategoryModel.get_by_id(data["category_id"]):
        raise NotFound(error_message="The specified category does not exist.")
    # Check if another item with the same name exists in the database.
    if ItemModel.get_by_name(data["name"]):
        raise ValueExistedError(error_data={"name": ["Name already exists."]})

    # Create new item and add to database.
    item = ItemModel(user_id, **data)
    db.session.add(item)
    db.session.commit()

    item_schema = ItemSchema()
    item_schema.context["authenticated_user_id"] = user_id
    return item_schema.dump(item)


@app.route("/items/<int:item_id>", methods=["PUT"])
@validate_request_body(schema_class=ItemSchema)
@authentication()
def edit_item(item_id, **kwargs):
    user_id = kwargs.get("user_id")  # id of logged-in user, None if guest.

    data = kwargs["data"]

    # Check if the category_id specified exists in the database
    if not CategoryModel.get_by_id(data["category_id"]):
        raise NotFound(error_message="The specified category does not exist.")

    # Check if another item with the same name but different id exists in the database.
    item = ItemModel.get_by_name(data["name"])
    if item and item_id != item.id:
        raise ValueExistedError(error_data={"name": ["Name already exists."]})

    # Check if the item with the specified_id exists in the database and if the
    # logged-in user owns it.
    item = ItemModel.get_by_id(item_id)
    if not item:
        raise NotFound(error_message="The specified item does not exist.")
    elif item.user_id != user_id:
        raise Forbidden(error_message="User does not have sufficient permissions.")

    # Update the item
    for key, value in data.items():
        setattr(item, key, value)
    db.session.add(item)
    db.session.commit()

    item_schema = ItemSchema()
    item_schema.context["authenticated_user_id"] = user_id
    return item_schema.dump(item)


@app.route("/items/<int:item_id>", methods=["DELETE"])
@authentication()
def delete_item(item_id, **kwargs):
    user_id = kwargs.get("user_id")  # id of logged-in user, None if guest.

    # Check if the category exists in the database
    item = ItemModel.get_by_id(item_id)
    if not item:
        raise NotFound(error_message="The specified item does not exist.")
    elif item.user_id != user_id:
        raise Forbidden(error_message="User does not have sufficient permissions.")
    else:
        db.session.delete(item)
    db.session.commit()

    return {}
