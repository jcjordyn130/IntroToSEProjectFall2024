import uuid
import time
import datetime
from flask import request
from functools import wraps

class Key():
    key = None
    username = None
    created = None
    lastused = None
    userlevel = None

    def __init__(self, username):
        self.key = uuid.uuid4().hex
        self.username = username
        self.created = int(time.time())
        self.lastused = None
        self.userlevel = None

        prettytime = datetime.datetime.fromtimestamp(self.created).isoformat()
        print(f"Created API key {self.key} for user {self.username} on {prettytime}")

    def __del__(self):
        if self.lastused:
            prettytime = datetime.datetime.fromtimestamp(self.lastused).isoformat()
        else:
            prettytime = "never"

        print(f"Removing API key {self.key} for user {self.username}, last used on {prettytime}")

    def __eq__(self, other):
        # Compare self.key values if the other comparison is a string
        # Call parent equal operator function otherwise.
        #
        # This makes the functions in APIKeyManager easier to implement,
        # but it also allows for list().remove("someapikeytoken") to work
        # without needing to fetch the entire Key class.
        if isinstance(other, str):
            return self.key == other
        else:
            super().__eq__(other)

    def __str__(self):
        return f"({self.username}) {self.key}"

    def __repr__(self):
        return self.__dict__.__repr__()

    def __hash__(self):
        return hash(self.key)
        
class APIKeyManager():
    def __init__(self, db):
        self.__keys__ = []
        self.db = db

    def __len__(self):
        return len(self.__keys__)

    def __repr__(self):
        return f"APIKeyManager | # of Keys: {len(self)}"

    def create(self, username):
        if not username:
            raise ValueError("username must not be False!")

        key = Key(username)

        # Add user level for easy usage in @api_key_required
        user = self.db.getUser(username = username)
        if not user:
            raise ValueError("Username was not found in database")
        key.userlevel = user.userlevel

        # Add API key
        self.__keys__.append(key)

        # Return API key
        return key

    def remove(self, key):
        self.__keys__.remove(key)

    def removeAllUserKeys(self, username):
        # We have to duplicate the values we want to remove as CPython does NOT
        # support removing from a list while iterating over it.
        userskeys = [x for x in self.__keys__ if x.username == username]
        for apikey in userskeys:
            self.__keys__.remove(apikey)

    def verify(self, key):
        # Check for key
        # Return True if we have the key or False if we don't
        try:
            apikey = self.__keys__[self.__keys__.index(key)]
            apikey.lastused = int(time.time())
            print(f"API Key {apikey} is being used!")
            return True
        except ValueError:
            return False

    def get(self, key):
        return self.__keys__[self.__keys__.index(key)]