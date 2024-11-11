from .. import database
import random
import faker
import bcrypt

numberofitems = 100
fakeusernames = {
    "admin": "admintestinguser",
    "seller": "sellertestinguser",
    "buyer": "buyertestinguser",
    "unapproved": "unapproveduser"
}

fakeemails = {
    "admin": "webmaster@localhost.local",
    "seller": "ProjectLLC@localhost.local",
    "buyer": "SomePerson@localhost.local",
    "unapproved": "spammer@scam.nmap"
}

fakeuserlevels = {
    "admin": database.dbtypes.UserLevel(1),
    "seller": database.dbtypes.UserLevel(2),
    "buyer": database.dbtypes.UserLevel(3),
    "unapproved": database.dbtypes.UserLevel(3)
}

fakepassword = "pA$$wOrD#$#$"

def generate_random_username():
    adjectives = ["happy", "blue", "clever", "swift", "fierce", "terminal", "insane", "clover", "smol"]
    nouns = ["cat", "dog", "bird", "tree", "river", "boi", "birb", "bird", "peep"]
    
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(0, 1000000)
    
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

def createTestingDB(dbpath = "db.sqlite3"):
    users = []
    admins = []
    sellers = []
    dbase = database.Database(dbpath)

    # Generate users
    # Generate a single password hash to use for all the users...
    # This isn't secure but is useful for testing.
    hash = bcrypt.hashpw(fakepassword.encode(), database.dbtypes.__bcrypt_salt__)

    # Add in testing users
    for key in fakeusernames:
        user = database.dbtypes.User()
        user.username = fakeusernames[key]
        user.email = fakeemails[key]
        user.__password__ = hash
        user.userlevel = fakeuserlevels[key]
        if key != "unapproved":
            user.approval = True
        else:
            user.approved = False
        dbase.commitUser(user)
        if user.userlevel == database.dbtypes.UserLevel.Admin:
            admins.append(user)
        elif user.userlevel == database.dbtypes.UserLevel.Seller:
            sellers.append(user)
        else:
            users.append(user)

    # Add in testing items
    for i in range(0, numberofitems):
        item = database.dbtypes.Item()
        n = random.randint(0, len(itemnames) - 1)
        item.name = itemnames[n]
        item.description = itemdescs[n]
        item.quantity = random.randint(0, 1776)
        item.seller = sellers[0].id
        # First 100 items are auto approved, good luck
        if i >= numberofitems / 2:
            item.approval = random.randint(0, 1)
        dbase.commitItem(item)

    # Add in random users, useful for API stress testing
    for i in range(0, numberofitems):
        while True:
            user = database.dbtypes.User()
            user.username = generate_random_username()
            user.email = f"{generate_random_username()}@gmail.com"
            user.approval = bool(random.randint(0, 1))
            if i in [0, 1, 2, 3, 4]:
                # We need at *least* one admin
                user.userlevel = database.dbtypes.UserLevel.Admin
                user.approval = True
            elif i in [5, 6, 7, 8, 9]:
                # Makes the following code easier
                user.userlevel = database.dbtypes.UserLevel.Seller
                user.approval = True
            else:
                user.userlevel = database.dbtypes.UserLevel(random.randint(1, 3))
            user.__password__ = hash # Setting the backing store because we already have a hashed password
            try:
                dbase.commitUser(user)
            except ValueError:
                print("Value collision... using another user for this iteration")
                continue
            users.append(user)
            if user.userlevel == database.dbtypes.UserLevel.Admin:
                admins.append(user)
            elif user.userlevel == database.dbtypes.UserLevel.Seller:
                sellers.append(user)
            break

    # Generate Items
    for i in range(0, numberofitems):
        item = database.dbtypes.Item()
        n = random.randint(0, len(itemnames) - 1)
        item.name = itemnames[n]
        item.description = itemdescs[n]
        item.quantity = random.randint(0, 1776)
        item.seller = random.choice(sellers + admins).id
        # First 100 items are auto approved, good luck
        if i >= 100:
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
