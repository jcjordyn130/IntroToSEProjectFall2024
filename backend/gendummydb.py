import database
import random
import faker
import bcrypt

numberofitems = 16384
# happytree499
fakeuserpw = "bluebird871"

""" gendummydatabase.dbtypes.py is a script to generate a dummy testing database for the project.
It uses mostly predetermined item names/descriptions while outsouring to the Faker library
for payment information. """

def generate_random_username():
    adjectives = ["happy", "blue", "clever", "swift", "fierce"]
    nouns = ["cat", "dog", "bird", "tree", "river"]
    
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(100, 999)
    
    username = f"{adjective}{noun}{number}"
    return username

itemnames = [
    "PlayStation 5",
    "PlayStation 5 (Digital Edition)"
    "PlayStation 4",
    "PlayStation 3",
    "PlayStation 2 SLIM",
    "PlayStation 1",
    "PSONE",
    "CTR Dev Kit",
    "Nintendo Switch SDEV",
    "Nitendo Switch NDEV",
    "RVL Dev Kit",
    "DDR4 RAM",
    "Dolphin Dev Kit"
]

itemdescs = [
    "PS5 Console with included optical disc drive attachment",
    "PS5 Console",
    "PS4 Console",
    "PS3 Console",
    "PS2 Console (Backwards Compatible with PS1/PSONE). Slim form factor. Uses less power and produces less heat.",
    "First Generation 3D Console from Sony. Revolutionized 3D gaming as we know it.",
    "Revision of the PlayStation 1. Runs cooler and avoids CDROM problems",
    "Development Kit for the Nintendo 3DS. All Rights Reserved.",
    "Testing Kit for Games Studios of the Nintendo Switch. All Rights Reserved.",
    "Development Kit for the Nintendo Switch. All Rights Reserved. INTERNAL Nintendo use ONLY",
    "Development Kit for the Nintendo Wii. All Rights Reserved. INTERNAL Nintendo use ONLY.",
    "Double Data Rate 4th Gen RAM for a Desktop PC. Unregistered. ECC Compatible.",
    "Development Kit for the Nintendo Gamecube. The predecessor of the Wii (Revolution). All Rights Reserved. INTERNAL Nintendo use ONLY."
]

users = []
dbase = database.Database("db.sqlite3")

# Generate users
# Generate a single password hash to use for all the users...
# This isn't secure but is useful for testing.
hash = bcrypt.hashpw(fakeuserpw.encode(), database.dbtypes.__bcrypt_salt__)

for i in range(0, numberofitems):
    while True:
        user = database.dbtypes.User()
        user.username = generate_random_username()
        user.email = f"{generate_random_username()}@gmail.com"
        if i == 0:
            # We need at *least* one admin
            user.userlevel = database.dbtypes.UserLevel.Admin
        elif i == 1:
            # Makes the following code easier
            user.userlevel = database.dbtypes.UserLevel.Seller
        else:
            user.userlevel = database.dbtypes.UserLevel(random.randint(0, 2))
        user.approval = bool(random.randint(0, 1))
        user.__password__ = hash # Setting the backing store because we already have a hashed password
        try:
            dbase.commitUser(user)
        except ValueError:
            print("Value collision... using another user for this iteration")
            continue
        users.append(user)
        break

# Generate Items
for i in range(0, numberofitems):
    item = database.dbtypes.Item()
    n = random.randint(0, len(itemnames) - 1)
    item.name = itemnames[n]
    item.description = itemdescs[n]
    item.quantity = random.randint(0, 12345)
    item.seller = users[1].id
    item.approval = random.randint(0, 1)
    dbase.commitItem(item)

# Generate payment methods
f = faker.Faker()
for i in range(0, numberofitems):
    pm = database.dbtypes.PaymentMethod()
    n = random.randint(0, len(users) - 1)
    pm.user = users[n].id
    pm.name = f.credit_card_provider()
    pm.cardno = f.credit_card_number()
    pm.cardexp = f.credit_card_expire()
    pm.cardcvv = f.credit_card_security_code()
    pm.billingaddress = f.address()
    dbase.commitPaymentMethod(pm)
