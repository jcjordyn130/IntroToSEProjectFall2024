from .dbtypes import User, Order, PaymentMethod, Item, UserLevel, OrderStatus, OrderItems

def UserRowFactory(cursor, row):
    fields = [column[0] for column in cursor.description]
    kv = {key: value for key, value in zip(fields, row)}
    usr = User()
    usr.id = kv["id"]
    usr.username = kv["username"]
    usr.__password__ = kv["password"]
    usr.email = kv["email"]
    usr.userlevel = UserLevel(kv["userlevel"])
    usr.approval = bool(kv["approval"])
    return usr

def OrderRowFactory(cursor, row):
    fields = [column[0] for column in cursor.description]
    kv = {key: value for key, value in zip(fields, row)}
    order = Order()
    order.id = kv["id"]
    order.user = kv["user"]
    order.orderstatus = OrderStatus(kv["orderstatus"])
    return order

def OrderItemsRowFactory(cursor, row):
    fields = [column[0] for column in cursor.description]
    kv = {key: value for key, value in zip(fields, row)}
    orderitems = OrderItems()
    orderitems.id = kv["id"]
    orderitems.order = kv["orderid"] # TODO: be consistent with order naming
    orderitems.item = kv["item"]
    orderitems.quantity = kv["quantity"]
    return orderitems


def PaymentMethodRowFactory(cursor, row):
    fields = [column[0] for column in cursor.description]
    kv = {key: value for key, value in zip(fields, row)}
    paymeth = PaymentMethod()
    paymeth.id = kv["id"]
    paymeth.user = kv["user"]
    paymeth.name = kv["name"]
    paymeth.cardno = kv["cardno"]
    paymeth.cardexp = kv["cardexp"]
    paymeth.cardcvv = kv["cardcvv"]
    return paymeth

def ItemRowFactory(cursor, row):
    fields = [column[0] for column in cursor.description]
    kv = {key: value for key, value in zip(fields, row)}
    item = Item()
    item.id = kv["id"]
    item.name = kv["name"]
    item.description = kv["description"]
    item.quantity = kv["quantity"]
    item.seller = kv["seller"]
    item.approval = bool(kv["approval"])
    return item
