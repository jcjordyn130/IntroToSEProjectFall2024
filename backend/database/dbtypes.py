
from enum import Enum
import uuid
import bcrypt
import copy

# Normally this is not a secure method of saving passwords.
__bcrypt_salt__ = b'$2b$16$2npL2FY08B03FPETzV0tse'

class UserLevel(Enum):
    Admin = 0
    Seller = 1
    Buyer = 2

    def __repr__(self):
        return f"UserLevel.{self.name}"

class OrderStatus(Enum):
    Unfulfilled = 0
    Fulfilled = 1
    Shipped = 2
    Arrived = 3

class User():
    id = None
    username = None
    email = None
    __password__ = None # Backing password store
    userlevel = None
    approval = False

    # I use password as a python property so passwords are hashed as soon as the property is set
    # This reduces the chances of a developer bug resulting in plain text passwords
    # __password__ is what stores the backing hash
    @property
    def password(self):
        return self.__password__

    @password.setter
    def password(self, value):
        self.__password__ = bcrypt.hashpw(value.encode(), __bcrypt_salt__)

    def __init__(self):
        self.id = uuid.uuid4().hex
        #print(f"Creating User class with id {self.id}")

    def __str__(self):
        return f"<{self.id}: {self.userlevel.name}, username = {self.username}, has password? = {self.password is not None}, mail = {self.email}, approved: {self.approval}>"

    def __repr__(self):
        # We use __repr__ to easily convert the class into a dict for the API
        # without having to reference easy variable.
        #
        # We can't just use __dict__ by itself because it'll send the password hash
        # over the internet which is insecure.
        safedict = copy.copy(self.__dict__)
        safedict.pop("__password__")
        #safedict["userlevel"] = safedict["userlevel"].value
        return safedict.__repr__()

    def verifyPassword(self, password):
        return bcrypt.checkpw(password.encode(), self.password)

class Order():
    id = None
    user = None
    orderstatus = None

    def __init__(self):
        self.id = uuid.uuid4().hex

    def __repr__(self):
        return f"<ID: {self.id}, user: {self.user}, orderstatus: {self.orderstatus.name}>"

class OrderItems():
    id = None
    order = None
    item = None
    quantity = 0

    def __init__(self):
        self.id = uuid.uuid4().hex

    def __repr__(self):
        return super().__repr__()

class PaymentMethod():
    id = None
    user = None
    name = None
    cardno = None
    cardexp = None
    cardcvv = None
    billingaddress = None
    
    def __init__(self):
        self.id = uuid.uuid4().hex

    def __repr__(self):
        # I don't print cardno/exp/cvv as it's sensitive information.
        return f"<ID: {self.id}, user: {self.user}, name: {self.name}>"

class Item():
    id = None
    name = None
    description = None
    quantity = 0
    seller = None
    approval = False

    def __init__(self):
        self.id = uuid.uuid4().hex

    def __repr__(self):
        return f"<ID: {self.id}, name: {self.name}, quantity: {self.quantity}>"