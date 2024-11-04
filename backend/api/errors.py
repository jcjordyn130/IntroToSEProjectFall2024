import copy

UserNotFound = ({"error": "ERRUSERNOTFOUND", "status": "err"}, 404)
WrongPassword = ({"error": "ERRWRONGPASSWORD", "status": "err"}, 401)
InvalidRequest = ({"error": "ERRINVALIDREQUEST", "status": "err"}, 400)
NotApproved = ({"error": "ERRNOTAPROVED", "status": "err"}, 403)
AuthorizationRequired = ({"error": "ERRNOTAUTHORIZED", "status": "err"}, 401)
ResourceAlreadyApproved = ({"error": "ERRRSRCALREADYAPPROVED", "status": "err"}, 400)
ResourceNotFound = ({"error": "ERRRSRCNOTFOUND", "status": "err"}, 404)
OutOfItem = ({"error": "ERROUTOFITEM", "status": "err"}, 400) # Used when adding more items to an order than we have

# These are all the standard fields, but other calls may have others.
# AddItemToOrder, for instance, returns onhandquantity and quantity when a ERROUTOFITEM error occurs
# to signal to the client how many of that item we have and how many were trying to be added.abs
#
# Format of an error:
# status: err if error, ok otherwise (all API responses will have a status)
# error: short string identifying error, typically in the format of ERR[someerror] such as ERRUSERNOTFOUND.
# exc: a dict containing exception info (other fields might be added later, but right now we just have the message)
#   msg: The exception message, non-localized
# extra: Extra data that can help in identifying errors to the user

""" exc() takes an exception and adds it in the standard format to an error. """
def exc(resp, exc):
    data = {"exc":{"msg": str(exc)}}
    return build(resp, data)

""" build() takes an error and adds arbitrary data onto it. """
def build(resp, data):
    if not isinstance(data, dict):
        raise ValueError("Data can only be a dict as it's passed to dict().update()!")
        
    response = copy.deepcopy(resp)
    response[0].update(data)
    return response