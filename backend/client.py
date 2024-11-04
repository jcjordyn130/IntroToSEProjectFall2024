import requests, requests.auth
from urllib.parse import urljoin

baseurl = "http://localhost:5000"
s = requests.session()

#user = input("Username: ")
#user = "happytree499" # Admin
user = "blueriver252" # non-admin

password = "bluebird871"

class BearerAuth(requests.auth.AuthBase):
	def __init__(self, token):
		self.token = token

	def __call__(self, r):
		r.headers["authorization"] = f"Bearer {self.token}"
		return r

def login(username, password):
	url = urljoin(baseurl, f"/user/{user}/login")
	print(f"Using URL {url} for REST call!")
	resp = s.post(url, json = {"password": password})
	json = resp.json()
	print(json)

	if json["status"] == "ok":
		s.auth = BearerAuth(json["apikey"])

def logout():
	if not s.auth:
		raise ValueError("You can't logout if you aren't logged int!")

	url = urljoin(baseurl, "/user/logout")
	resp = s.get(url)
	json = resp.json()
	print(json)
	s.auth = None
	if json["status"] == "ok":
		return True
	else:
		return json["error"]

def approveUser(username):
	if not s.auth:
		raise ValueError("You must be authenticated!")

	url = urljoin(baseurl, f"/admin/approveUser/{username}")
	resp = s.get(url)
	json = resp.json()
	print(json)
	if json["status"] == "ok":
		return True
	else:
		return json["error"]

def getUserInfo(username = None):
	if username:
		url = urljoin(baseurl, f"/user/info/{username}")
		print(url)
	else:
		url = urljoin(baseurl, f"/user/info")

	resp = s.get(url)
	json = resp.json()
	return json

def createOrder():
	if not s.auth:
		raise ValueError("Must be authenticated!")

	url = urljoin(baseurl, "/order/create")
	resp = s.post(url)
	json = resp.json()
	print(json)
	return json

def deleteOrder(id):
	if not s.auth:
		raise ValueError("Must be authenticated")

	url = urljoin(baseurl, f"/order/{id}/delete")
	resp = s.delete(url)
	json = resp.json()
	print(json)
	return json["status"] == "ok"

def addItemsToOrder(order, item, quantity):
	url = urljoin(baseurl, f"/order/{order}/add/{item}/{quantity}")
	resp = s.post(url)
	json = resp.json()
	print(json)
	return json["status"] == "ok"

login(user, password)
print(getUserInfo())
order = createOrder()
item = input("Item to add: ")
quantity = input("Quantity of items to add: ")
print(addItemsToOrder("d58518463ad34620a1895025fdc634a5", item, quantity))
#user = input("User to approve: ")
#approveUser(user)
#print(getUserInfo())
#print(getUserInfo("swiftriver821"))
#order = createOrder()
#deleteOrder(order["id"])
#deleteOrder("03fe2d47d660427b95dc0b4a1d2dc6cd") # admins order
logout()
