import sqlite3
import uuid
import threading
from .rowfactories import *
from .dbtypes import *

""" The Database class represents a database connection.
It stores the underlying sqlite3 connection and creates necessary tables
at startup.
"""
class Database():
    @property
    def cur(self):
        # This is just a nice way to grab a cursor for our clients
        return self.conn.cursor()

    def __init__(self, dbfile):
            # check_same_thread is disabled as SQLite3 has some internal locking to avoid
            # multithreading corrupting the database.
            # Additionally, every DB access below is protected with a threading lock,
            # for extra assurance against data corruption.
            self.conn = sqlite3.connect(dbfile, check_same_thread = False, autocommit = True)
            # SQLite3 does NOT support concurrent write access and sometimes
            # SQLite3's internal locks cause a SQL ERROR, so we handle locking here.
            self._lock = threading.Lock()
            self.initDB()

    def __del__(self):
        # Commit the database transaction when this class is destroyed.
        # This protects against accidently left open commits
        try:
            self.conn.commit()
        except AttributeError:
            # Ignore AttributeErrors as __del__ can be called before __init__ finishes
            pass

    def initDB(self):
        print("Creating database tables...")
        with self._lock:
            self.cur.execute("CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, username TEXT UNIQUE, password TEXT NOT NULL, email TEXT UNIQUE, userlevel INTEGER, approval INTEGER)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, user TEXT, orderstatus INTEGER)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS orderitems(id TEXT, orderid TEXT, item TEXT, quantity INTEGER)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS paymentmethods(id TEXT PRIMARY KEY, user TEXT, name STRING, cardno INTEGER UNIQUE, cardexp TEXT, cardcvv TEXT, billingaddress TEXT)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS items(id TEXT PRIMARY KEY, name TEXT, description TEXT, quantity INTEGER, seller TEXT, approval INTEGER)")
    
    def getUser(self, id = None, username = None, email = None):
        optVars = [id is None, username is None, email is None]
        if len([x for x in optVars if x == False]) != 1:
            raise ValueError("id, username, and email are mutually exclusive arguments!")

        with self._lock:
            cur = self.cur
            cur.row_factory = UserRowFactory

            if id:
                cur.execute("SELECT * FROM users WHERE id = ?", (id,))
            elif username:
                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            elif email:
                cur.execute("SELECT * FROM users WHERE email = ?", (email,))

            return cur.fetchone()

    def commitUser(self, user):
        print(f"Commiting user {user} to database!")

        # Check for user
        if self.getUser(username = user.username) or self.getUser(email = user.email):
            raise ValueError("Duplicate usernames and emails are NOT allowed!")

        if self.getUser(id = user.id):
            raise ValueError("Duplicate IDs are NOT allowed! Use updateUser() to update.")

        if user.password is None:
            raise ValueError("User MUST have a password... even if temporary!")

        with self._lock:
            self.cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)", (
                user.id,
                user.username,
                user.password,
                user.email,
                user.userlevel.value,
                user.approval
            ))

    def updateUser(self, user):
        with self._lock:
            self.cur.execute("UPDATE users SET id = ?, username = ?, password = ?, email = ?, userlevel = ?, approval = ? WHERE id = ?", (
                user.id,
                user.username,
                user.password,
                user.email,
                user.userlevel.value,
                user.approval,
                user.id
            ))

    def getItem(self, id):
        with self._lock:
            cur = self.cur
            cur.row_factory = ItemRowFactory
            cur.execute("SELECT * FROM items WHERE id = ?", (id,))
            return cur.fetchone()

    def getItemsBySeller(self, seller):
        # Check for seller's user account
        if not self.getUser(id = seller):
            raise ValueError(f"Seller ID {seller} does not exist!")

        with self._lock:
            cur = self.cur
            cur.row_factory = ItemRowFactory
            cur.execute("SELECT * FROM items WHERE seller = ?", (seller,))
            return cur.fetchall()

    def commitItem(self, item):
        print(f"Commiting item {item} to database!")

        # Check for seller's user account
        if not self.getUser(id = item.seller):
            raise ValueError(f"Seller ID on item {item} does not exist!")

        with self._lock:
            self.cur.execute("INSERT INTO items VALUES(?, ?, ?, ?, ?, ?)", (
                item.id,
                item.name,
                item.description,
                item.quantity,
                item.seller,
                item.approval
            ))

    def updateItem(self, item):
        # Check for seller's user account
        if not self.getUser(id = item.seller):
            raise ValueError(f"Seller ID on item {item} does not exist!")

        # Check for existing item
        if not self.getItem(id = item.id):
            raise ValueError(f"Item ID on item {item} does not exist!")

        with self._lock:
            self.cur.execute("UPDATE items SET id = ?, name = ?, description = ?, quantity = ?, seller = ?, approval = ? WHERE id = ?", (
                item.id,
                item.name,
                item.description,
                item.quantity,
                item.seller,
                item.approval,
                item.id
            ))

    def getOrder(self, id):
        with self._lock:
            cur = self.cur
            cur.row_factory = OrderRowFactory
            cur.execute("SELECT * FROM orders WHERE id = ?", (id,))
            return cur.fetchone()

    def commitOrder(self, order):
        print(f"Commiting order {order} to database!")

        # Check for user account
        if not self.getUser(id = order.user):
            raise ValueError(f"User ID on order {order} does not exist!")

        with self._lock:
            self.cur.execute("INSERT INTO orders VALUES(?, ?, ?)", (
                order.id,
                order.user,
                order.orderstatus.value
            ))

    def addItemToOrder(self, order, item, quantity = 1):
        print(f"Adding item {item} to order {order}!")
        # These checks mainly exist to strengthen database references
        # As a client can create the dbtypes and give it to these functions.
        #
        # TODO: make foreign keys to make it a SQL constrait
        # Check for order
        if not self.getOrder(id = order.id):
            raise ValueError(f"Order {order} does not exist in the database!")

        # Check for item
        if not self.getItem(id = item.id):
            raise ValueError(f"Item {item} does not exist in the database!")

        # Make sure we aren't adding more than we already have
        if quantity > item.quantity:
            raise OverflowError(f"Order quantity {quantity} is more than the on hand count {item.quantity}")

        # Database stuffes
        with self._lock:
            # Check for existing order item
            cur = self.cur
            cur.row_factory = OrderItemsRowFactory
            cur.execute("SELECT * FROM orderitems WHERE orderid = ? AND item = ?", (order.id, item.id))
            orderitem = cur.fetchone()

            # Make sure we don't order more than we have
            if orderitem:
                if orderitem.quantity + quantity > item.quantity:
                    raise OverflowError(f"New order quantity {orderitem.quantity + quantity} is more than the on hand count {item.quantity}")

                self.cur.execute("UPDATE orderitems SET quantity = ? WHERE id = ?", (orderitem.quantity + quantity, orderitem.id))
            else:
                orderitem = OrderItems()
                orderitem.order = order.id
                orderitem.item = item.id
                orderitem.quantity = quantity
                self.cur.execute("INSERT INTO orderitems VALUES(?, ?, ?, ?)", (
                    orderitem.id,
                    orderitem.order,
                    orderitem.item,
                    orderitem.quantity
                ))
        
    def deleteOrder(self, order):
        print(f"Deleting order {order} from database!")

        if not self.getOrder(order.id):
            raise ValueError(f"Order with ID {order} does not exist!")

        with self._lock:
            self.cur.execute("DELETE FROM orders WHERE id = ?", (order.id,))

    def updateOrder(self, order):
        # Check for order
        if not self.getOrder(id = order.id):
            raise ValueError("Order ID on order {order} does not exist!")

        with self._lock:
            self.cur.execute("UPDATE orders SET id = ?, user = ?, orderstatus = ? WHERE id = ?", (
                order.id,
                order.user,
                order.orderstatus.value,
                order.id
            ))

    def getPaymentMethod(self, id):
        with self._lock:
            cur = self.cur
            cur.row_factory = PaymentMethodRowFactory
            cur.execute("SELECT * FROM paymentmethods WHERE id = ?", (id,))
            return cur.fetchone()

    def commitPaymentMethod(self, pm):
        print(f"Commiting payment method {pm} to database!")

        # Check for user account
        if not self.getUser(id = pm.user):
            raise ValueError(f"User ID on payment method {pm} does not exist!")

        with self._lock:
            self.cur.execute("INSERT INTO paymentmethods VALUES(?, ?, ?, ?, ?, ?, ?)", (
                pm.id,
                pm.user,
                pm.name,
                pm.cardno,
                pm.cardexp,
                pm.cardcvv,
                pm.billingaddress
            ))

    def updatePaymentMethod(self, pm):
        # Check for user account
        if not self.getUser(id = pm.user):
            raise ValueError(f"User ID on payment method {pm} does not exist!")

        # Check for payment method
        if not self.getPaymentMethod(id = pm.id):
            raise ValueError(f"Payment Method ID on payment method {pm} does not exist!")

        with self._lock:
            self.cur.execute("UPDATE paymentmethods SET id = ?, user = ?, name = ?, cardno = ?, cardexp = ?, cardcvv = ?, billingaddress = ? WHERE id = ?", (
                pm.id,
                pm.user,
                pm.name,
                pm.cardno,
                pm.cardexp,
                pm.cardcvv,
                pm.billingaddress,
                pm.id
            ))
