from flask import Flask, request, jsonify
from .. import database
from . import errors, responses, keymanager
from ..database.dbtypes import *
from functools import wraps
import copy

app = Flask(__name__)
db = database.Database("db.sqlite3")
km = keymanager.APIKeyManager(db)

def api_key_required(level):
    def ad(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: check for auth type = Bearer
            
            # Check for authorization header and make sure it is correct
            if not request.authorization:
                return errors.AuthorizationRequired

            # Authorization.data can be None when the parent type is not... idk why, but that's what the API docs say.
            if not request.authorization.token:
                return errors.AuthorizationRequired

            # Final check
            if not km.verify(request.authorization.token):
                print(f"API Call attempted with invalid API key!")
                return errors.AuthorizationRequired

            # We have the API key, now check the level
            key = km.get(request.authorization.token)
            if key.userlevel.value > level.value:
                print(f"UserLevel required for this function is {level} but we have {key.userlevel}!")
                return errors.AuthorizationRequired

            return f(*args, **kwargs)

        return decorated_function

    return ad

@app.route("/")
def whatwhoisthis():
    return "There is nothing to see here. <br> <b> Move along. </b>"

@app.route("/user/<username>/login", methods = ["GET", "POST"])
def login(username):
    data = request.json

    # Check for blank passwords and fail early as blank passwords are NOT allowed.
    # As they aren't allowed, they wouldn't be in the database anyways so don't waste time hashing.
    if not data.get("password", None):
        return errors.InvalidRequest

    user = db.getUser(username = username)
    if not user:
        return errors.UserNotFound

    # Make sure the user is verified before we allow login
    if not user.approval:
        return errors.NotApproved

    if user.verifyPassword(data["password"]):
        # Create API Key
        key = km.create(username)
        return responses.build(responses.GenericOK, {"apikey": key.key})
    else:
        return errors.WrongPassword

@app.route("/user/logout")
@api_key_required(level = UserLevel.Buyer)
def logout():
    # Do the thing
    km.remove(request.authorization.token)
    return responses.GenericOK

@app.route("/user/logouteverywhere")
@api_key_required(level = UserLevel.Buyer)
def killkeys():
    key = km.get(request.authorization.token)
    km.removeAllUserKeys(key.username)
    return responses.GenericOK

@app.route("/user/info/<username>")
@app.route("/user/info")
@api_key_required(level = UserLevel.Buyer)
def userinfo(username = None):
    key = km.get(request.authorization.token)

    # If we have a explicit username, check for admin privs first.
    if username:
        if key.userlevel != UserLevel.Admin:
            return errors.ResourceNotFound
    else:
        username = key.username

    user = db.getUser(username = username)
    if not user:
        return errors.ResourceNotFound
    
    return jsonify(repr(user))

@app.route("/admin/approveUser/<username>")
@api_key_required(level = UserLevel.Admin)
def approveUser(username):
    # Lookup user
    user = db.getUser(username = username)
    if not user:
        return errors.UserNotFound

    # Set approval
    if not user.approval:
        user.approval = True
    else:
        return errors.ResourceAlreadyApproved

    # Update user in database
    db.updateUser(user)

    # Return goooood
    return responses.GenericOK

@app.route("/order/create", methods = ["POST"])
@api_key_required(level = UserLevel.Buyer)
def createOrder():
    # Grab key so we can get the username
    key = km.get(request.authorization.token)

    # Grab user so we can get the ID
    user = db.getUser(username = key.username)

    # Create Order() and fill in data
    order = Order()
    order.orderstatus = OrderStatus.Unfulfilled
    order.user = user.id

    # Commit to DB
    db.commitOrder(order)

    # Return ID
    return responses.build(responses.GenericOK, {"id": order.id, "username": key.username, "status": order.orderstatus.value})

@app.route("/order/<id>/delete", methods = ["DELETE"])
@api_key_required(level = UserLevel.Buyer)
def deleteOrder(id):
    # Grab key so we can get the username
    key = km.get(request.authorization.token)

    # Grab user so we can get the ID
    user = db.getUser(username = key.username)

    # Grab order from DB
    order = db.getOrder(id)
    if not order:
        return errors.ResourceNotFound

    # Return not found if user is not an admin and order is does not belong to them.
    if order.user != user.id and user.userlevel != UserLevel.Admin:
        print(f"Non-admin user {user} attempted to delete order {order}!")
        return errors.ResourceNotFound

    # Delete it
    db.deleteOrder(order)

    # Return ok.
    return responses.GenericOK

@app.route("/order/<id>/add/<itemid>/<int:quantity>", methods = ["POST"])
@api_key_required(level = UserLevel.Buyer)
def addItemsToOrder(id, itemid, quantity):
    # Grab key so we can get the username
    key = km.get(request.authorization.token)

    # Grab user so we can get the ID
    user = db.getUser(username = key.username)

    # Grab order from DB
    order = db.getOrder(id)
    if not order:
        return errors.ResourceNotFound

    # Return not found if user is not an admin and order is does not belong to them.
    if order.user != user.id and user.userlevel != UserLevel.Admin:
        print(f"Non-admin user {user} attempted to delete order {order}!")
        return errors.ResourceNotFound

    # Grab item
    item = db.getItem(itemid)
    if not item:
        return errors.ResourceNotFound

    # Add items
    try:
        db.addItemToOrder(order, item, quantity = quantity)
    except OverflowError as e:
        err = errors.build(errors.OutOfItem, {"extra": {"quantity": quantity, "onhandquantity": item.quantity}})
        return errors.exc(err, e)

    return responses.GenericOK