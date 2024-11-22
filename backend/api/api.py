from flask import Flask, request, jsonify, Request
import flask_cors

from .. import database
from . import errors, responses, keymanager
from ..database.dbtypes import *
from functools import wraps
import copy
from werkzeug.exceptions import *
# These are up here instead of by api_key_required even though it makes more sense
# As it has to be before the app init code.
class CustomRequest(Request):
    """ CustomRequest adds our in-house API key management to Flask requests.

    If an API key requiring endpoint is called and the API key is valid, then
    the API key and user database object are autopopulated in the request.

    This reduces boilerplate code in each API call associates with keeping up
    authentication state.
    """

    """ The currently logged in user associated with the request, if any. """
    user = None

    """ The current API key associated with the request, if any. 
    Any key set here is known to be valid as the decorator
    verifies the key.
    """
    key = None

class CustomFlask(Flask):
    request_class = CustomRequest

app = CustomFlask(__name__)
flask_cors.CORS(app)

#db = database.Database("db.sqlite3")
#km = keymanager.APIKeyManager(db)

def run(dbfile, *args, **kwargs):
    global db
    global km

    print(f"Using file {dbfile} for database!")
    db = database.Database(dbfile)
    km = keymanager.APIKeyManager(db)

    app.run(*args, **kwargs)

@app.errorhandler(Exception)
def handle_exc(e):
    # pass through HTTP exceptions
    if isinstance(e, HTTPException):
        return e

    # Otherwise, return them as a JSON error
    return errors.exc(errors.UnknownException, e)

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

            # Grab user to add to request.
            user = db.getUser(username = key.username)
            if not user:
                return errors.UserNotFound
            
            # key is good and level is good, add deets to the request.
            request.key = key
            request.user = user

            return f(*args, **kwargs)

        return decorated_function

    return ad

@app.route("/")
def whatwhoisthis():
    return "There is nothing to see here. <br> <b> Move along. </b>"

@app.route("/debug/km")
def debug_km():
    strs = [f"Key Manager: {km}", "Keys: "]
    for key in km.__keys__:
        strs.append(repr(key))

    return "<br>".join(strs)

@app.route("/debug/db")
def debug_db():
    items = db.countItems()
    orderitems = db.countOrderItems()
    orders = db.countOrders()
    pms = db.countPaymentMethods()
    users = db.countUsers()
    total = items + orderitems + orders + pms + users
    strs = [f"Items: {items}", f"Order Items: {orderitems}", f"Orders: {orders}", f"Payment Methods: {pms}", f"Users: {users}", f"Total: {total}"]
    return "<br>".join(strs)
    
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

@app.route("/user/<username>/create", methods = ["POST"])
def createUser(username):
    try:
        data = request.json
    except BadRequest as e:
        return errors.exc(errors.InvalidRequest, e)

    # Check for existing user
    if db.getUser(username = username):
        return errors.AlreadyExists

    # Check for required details
    try:
        data["email"]
        data["password"]
        data["userlevel"]
    except KeyError as e:
        return errors.build(errors.MissingArgument, {"argument": e.args[0]})

    # Create user
    user = User()
    user.username = username
    user.email = data["email"]
    user.password = data["password"] # Is hashed by the property value
    try:
        user.userlevel = UserLevel(data["userlevel"])
    except ValueError as e:
        return errors.exc(errors.InvalidRequest, e)

    # Commit to DB
    db.commitUser(user)

    return responses.GenericOK

@app.route("/user/list", methods = ["GET"])
@api_key_required(level = UserLevel.Admin)
def listUsers():
    # Get users
    users = db.getAllUsers()
    users = [repr(x) for x in users]

    # Return
    return responses.build(responses.GenericOK, {"users": users})

@app.route("/user/logout")
@api_key_required(level = UserLevel.Buyer)
def logout():
    # Do the thing
    km.remove(request.authorization.token)
    return responses.GenericOK

@app.route("/user/logouteverywhere")
@api_key_required(level = UserLevel.Buyer)
def killkeys():
    km.removeAllUserKeys(request.key.username)
    return responses.GenericOK

@app.route("/user/modify/<username>", methods = ["PATCH"])
@app.route("/user/modify", methods = ["PATCH"])
@api_key_required(level = UserLevel.Buyer)
def modifyUser(username = None):
    # Check for admin privs if we were given a username that is not ourselves.
    if username and username != request.user.username:
        # Don't let nonadmins modify other users
        if request.key.userlevel != UserLevel.Admin:
            return errors.ResourceNotFound
    else:
        username = request.key.username

    # Check for user
    user = db.getUser(username = username)
    if not user:
        return errors.ResourceNotFound

    # Check for params
    try:
        data = request.json
    except BadRequest as e:
        return errors.exc(errors.InvalidRequest, e)

    # Set params
    if data.get("email", None):
        user.email = data["email"]

    if data.get("password", None):
        user.password = data["password"]

    if data.get("userlevel", None):
        # Only allow UserLevel modification by admins
        if request.key.userlevel == UserLevel.Admin:
            user.userlevel = UserLevel(data["userlevel"])    
        else:
            return errors.AuthorizationRequired

    # Commit to DB
    db.updateUser(user)

    # Return OK
    return responses.GenericOK

@app.route("/user/info/<username>")
@app.route("/user/info")
@api_key_required(level = UserLevel.Buyer)
def userinfo(username = None):
    # If we have a explicit username, check for admin privs first.
    if username:
        if request.key.userlevel != UserLevel.Admin:
            return errors.ResourceNotFound
        else:
            user = db.getUser(username = username)
            if not user:
                return errors.ResourceNotFound
    else:
        user = request.user

    return responses.build(responses.GenericOK, {"users": [user]})
    #return jsonify(user)
    #return jsonify(repr(user))
    #return responses.build(responses.GenericOK, user)

@app.route("/user/<username>/approve")
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

@app.route("/user/<username>/unapprove")
@api_key_required(level = UserLevel.Admin)
def unapproveUser(username):
    # Lookup user
    user = db.getUser(username = username)
    if not user:
        return errors.UserNotFound

    # Set approval
    if not user.approval:
        return errors.NotApproved
    else:
        user.approval = False

    # Update user in database
    db.updateUser(user)

    # Return goooood
    return responses.GenericOK

@app.route("/order/create", methods = ["POST"])
@api_key_required(level = UserLevel.Buyer)
def createOrder():
    # Create Order() and fill in data
    order = Order()
    order.orderstatus = OrderStatus.Unfulfilled
    order.user = request.user.id

    # Commit to DB
    db.commitOrder(order)

    # Return ID
    return responses.build(responses.GenericOK, {"id": order.id, "username": request.key.username, "orderstatus": order.orderstatus.value})

@app.route("/order/<id>/delete", methods = ["DELETE"])
@api_key_required(level = UserLevel.Buyer)
def deleteOrder(id):
    # Grab order from DB
    order = db.getOrder(id)
    if not order:
        return errors.ResourceNotFound

    # Return not found if user is not an admin and order is does not belong to them.
    if order.user != request.user.id and request.user.userlevel != UserLevel.Admin:
        print(f"Non-admin user {request.user} attempted to delete order {order}!")
        return errors.ResourceNotFound

    # Delete it
    db.deleteOrder(order)

    # Return ok.
    return responses.GenericOK

@app.route("/order/<id>/add/<itemid>/<int:quantity>", methods = ["POST"])
@api_key_required(level = UserLevel.Buyer)
def addItemsToOrder(id, itemid, quantity):
    # Grab order from DB
    order = db.getOrder(id)
    if not order:
        return errors.ResourceNotFound

    # Return not found if user is not an admin and order is does not belong to them.
    if order.user != request.user.id and request.user.userlevel != UserLevel.Admin:
        print(f"Non-admin user {user} attempted to manage order {order}!")
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

@app.route("/order/<id>/delete/<itemid>/<int:quantity>", methods = ["DELETE"])
@api_key_required(level = UserLevel.Buyer)
def removeItemsFromOrder(id, itemid, quantity):
    # Grab order from DB
    order = db.getOrder(id)
    if not order:
        return errors.ResourceNotFound

    # Return not found if user is not an admin and order is does not belong to them.
    if order.user != request.user.id and request.user.userlevel != UserLevel.Admin:
        print(f"Non-admin user {user} at atempted to manage order {order}!")
        return errors.ResourceNotFound

    # Grab item
    item = db.getItem(itemid)
    if not item:
        return errors.ResourceNotFound

    # Remove items
    db.removeItemsFromOrder(order, item, quantity = quantity)

    return responses.GenericOK

@app.route("/order/<id>/info", methods = ["GET"])
@api_key_required(level = UserLevel.Buyer)
def grabOrderInfo(id):
    # Grab order from DB
    order = db.getOrder(id)
    if not order:
        return errors.ResourceNotFound

    # Return not found if user is not an admin and order is does not belong to them.
    if order.user != request.user.id and request.user.userlevel != UserLevel.Admin:
        print(f"Non-admin user {user} at atempted to manage order {order}!")
        return errors.ResourceNotFound

    # Grab items
    items = db.getItemsFromOrder(order)
    formatteditems = [{"id": x.item, "quantity": x.quantity} for x in items]

    # return info
    return responses.build(responses.GenericOK, {"id": order.id,
    "user": order.user,
    "orderstatus": order.orderstatus.value,
    "items": formatteditems})

@app.route("/payment/<name>/create", methods = ["POST"])
@api_key_required(level = UserLevel.Buyer)
def createPaymentMethod(name):
    # Create skeleton payment method
    pm = PaymentMethod()
    pm.user = request.user.id
    pm.name = name

    # Check for params
    try:
        data = request.json
    except BadRequest as e:
        return errors.exc(errors.InvalidRequest, e)

    # Set params
    try:
        # Validate params
        if len(data["cardcvv"]) > 4:
            return errors.build(errors.InvalidRequest, {"msg": "cardcvv len > 4"})

        if len(data["cardno"]) > 19:
            # NOTE: 19 max card length may change! See https://en.wikipedia.org/wiki/Payment_card_number
            return errors.build(errors.InvalidRequest, {"msg": "cardno len > 19"})

        pm.cardno = data["cardno"]
        pm.cardexp = data["cardexp"]
        pm.cardcvv = data["cardcvv"]
        pm.billingaddress = data["billingaddress"]
    except KeyError as e:
        return errors.exc(errors.MissingArgument, e)

    # Check for existing payment method
    if db.getPaymentMethod(cardno = data["cardno"]):
        return errors.AlreadyExists

    # Commit to DB
    db.commitPaymentMethod(pm)

    # OK
    return responses.GenericOK

@app.route("/payment/<id>/remove", methods = ["DELETE"])
@api_key_required(level = UserLevel.Buyer)
def removePaymentMethod(id):
    # Grab payment method to make sure it exists
    if not db.getPaymentMethod(id = id):
        return errors.ResourceNotFound

    # Remove it
    db.removePaymentMethod(id)
    
    # Return OK
    return responses.GenericOK

@app.route("/payment/list", methods = ["GET"])
@api_key_required(level = UserLevel.Buyer)
def grabPaymentMethods():
    # Grab payment methods
    pms = db.getPaymentMethodsByUser(user = request.user.id)

    # Return them
    return responses.build(responses.GenericOK, {"paymentmethods": pms})

@app.route("/item/add", methods = ["POST"])
@api_key_required(level = UserLevel.Seller)
def addItem():
    # Check for params
    try:
        data = request.json
    except BadRequest as e:
        return errors.exc(errors.InvalidRequest, e)

    # Create item
    item = Item()

    # Fill in values, these are all required!!!
    try:
        item.name = data["name"]
        item.description = data["description"]
        item.quantity = int(data["quantity"])
        if request.key.userlevel == UserLevel.Admin and data.get("seller", None):
            item.seller = data["seller"]
        else:
            item.seller = request.user.id
        item.approval = False
    except KeyError as e:
        return errors.exc(errors.MissingArgument, e)
    except ValueError as e:
        return errors.exc(errors.InvalidRequest, e)
        
    # Commit to database
    db.commitItem(item)

    # OK
    return responses.GenericOK

@app.route("/item/list/<seller>", methods = ["GET"])
@app.route("/item/list", methods = ["GET"])
@api_key_required(level = UserLevel.Buyer)
def listItems(seller = None):
    # Grab seller user
    # If we aren't given a seller, list our items
    if seller:
        user = db.getUser(username = seller)
    else:
        user = request.user
    if not user:
        return errors.UserNotFound

    # Grab items
    items = db.getItemsBySeller(user.id)

    return responses.build(responses.GenericOK, {"items": items})

@app.route("/item/<id>/remove/<int:quantity>", methods = ["DELETE"])
@app.route("/item/<id>/remove", methods = ["DELETE"])
@api_key_required(level = UserLevel.Seller)
def deleteItem(id, quantity = None):
    # Fetch item from database
    item = db.getItem(id)
    if not item:
        return errors.ResourceNotFound

    # Only admins can remove items that do not belong to them
    # api_key_required checks for the minimum required level of Seller
    if item.seller != request.user.id and request.key.userlevel != UserLevel.Admin:
        return errors.AuthorizationRequired

    # Decrement item
    if quantity:
        item.quantity = item.quantity - quantity
        if item.quantity <= 0:
            print(f"Removing item {item} due to quantity falling to zero!")
            db.removeItem(item)
            return responses.GenericOK
    else:
        print(f"Removing item {item} due to no quantity given!")
        db.removeItem(item)
        return responses.GenericOK
    
    # Commit to DB
    db.updateItem(item)

    # OK
    return responses.GenericOK

@app.route("/item/<id>/approve")
@api_key_required(level = UserLevel.Admin)
def approveItem(id):
    # Lookup item
    item = db.getItem(id)
    if not item:
        return errors.ResourceNotFound

    # Set approval
    if not item.approval:
        item.approval = True
    else:
        return errors.ResourceAlreadyApproved

    # Update item in database
    db.updateItem(item)

    # Return goooood
    return responses.GenericOK

@app.route("/item/<id>/unapprove")
@api_key_required(level = UserLevel.Admin)
def unapproveItem(id):
    # Lookup item
    item = db.getItem(id)
    if not item:
        return errors.ResourceNotFound

    # Set approval
    if item.approval:
        item.approval = False
    else:
        return errors.NotApproved

    # Update item in database
    db.updateItem(item)

    # Return goooood
    return responses.GenericOK


if __name__ == "__main__":
    app.run(host = "127.0.0.1", port = "5000", debug = True)
