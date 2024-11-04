import uuid

class APIKeyManager():
    def __init__(self):
        self.__keys__ = {}

    def __len__(self):
        cnt = 0
        for username in self.__keys__:
            cnt+=len(self.__keys__[username])
        return cnt

    def create(self, username):
        key = uuid.uuid4().hex
        print(f"Created API key {key} for user {username}!")

        # Add username list in keys if it doesn't already exist
        try:
            self.__keys__[username]
        except KeyError:
            self.__keys__.update({username: []})

        # Add API key
        self.__keys__[username].append(key)

        # Return API key
        return key

    def remove(self, username, key = None):
        if key:
            print(f"Removing API key {key} for user {username}!")
        else:
            print(f"Removing ALL API keys for user {username}!")
            
        # Check for user list
        try:
            self.__keys__[username]
        except KeyError:
            raise ValueError(f"User {username} has no API keys to remove!")

        # Remove key if we have one
        # This raises ValueError if the key does not exist
        if key:
            self.__keys__[username].remove(key)
        else:
            # If we don't have a key, remove the ENTIRE users' keys
            self.__keys__[username] = []

    def verify(self, username, key):
        # Check for user list
        try:
            self.__keys__[username]
        except KeyError:
            # The user list does not exist yet... were we called too early?
            return False

        # Check for key
        # Return True if we have the key or False if we don't
        return key in self.__keys__[username]