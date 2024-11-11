import pytest
from ..api import api, errors, responses
import requests
import threading
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from . import gentestingdb as gtd

serverurl = "http://localhost:5000"

#### Custom Test Fixtures ####
@pytest.fixture(scope = "module")
def setup_api(tmp_path_factory):
    # Generate testing database
    dbfile = tmp_path_factory.mktemp("db") / "testing.db"
    gtd.createTestingDB(dbfile)

    # Start server in another thread, Flask's app.run blocks
    thread = threading.Thread(target = api.run, args = (dbfile, ), kwargs = {"debug": True, "use_reloader": False})
    thread.daemon = True
    thread.start()

    # Wait on it to be ready by checking the sus call
    s = requests.session()
    s.mount(serverurl, HTTPAdapter(max_retries = Retry(total = 1776, backoff_factor = 0.5)))

    while True:
        resp = s.get(serverurl)
        if resp.status_code == 200:
            break

    # Must yield something, so make it the thread
    yield dbfile

def assert_err(resp, error):
    assert resp.status_code == error[1]
    assert resp.json()["status"] == error[0]["status"]
    assert resp.json()["error"] == error[0]["error"]

def assert_ok(httpresp, apiresp):
    assert httpresp.status_code == apiresp[1]
    assert httpresp.json()["status"] == apiresp[0]["status"]

def login(username, password):
    resp = requests.post(f"{serverurl}/user/{username}/login", json = {"password": password})
    assert_ok(resp, responses.GenericOK)
    return resp.json()["apikey"]

class BearerAuth(requests.auth.AuthBase):
	def __init__(self, token):
		self.token = token

	def __call__(self, r):
		r.headers["authorization"] = f"Bearer {self.token}"
		return r

#### Generic Flask Tests ####
def test_api_invalidpath(setup_api):
    resp = requests.get(f"{serverurl}/user/this/is/not/a/real/path/obviously")
    assert resp.status_code == 404 

def test_api_invalidmethod(setup_api):
    resp = requests.patch(f"{serverurl}/user/{gtd.fakeusernames['admin']}/login", json = {"password": gtd.fakepassword})
    assert resp.status_code == 405 # HTTP Invalid Method

#### Login Tests ####
def test_login_missinguser(setup_api):
    resp = requests.post(f"{serverurl}/user/tHiSUsERDoEsNoTExIsTObViOuSlY/login", json = {"password": "doesntmatter"})
    assert_err(resp, errors.UserNotFound)

def test_login_wrongpassword(setup_api):
    resp = requests.post(f"{serverurl}/user/{gtd.fakeusernames['buyer']}/login", json = {"password": "wrongpa$$woRd"})
    assert_err(resp, errors.WrongPassword)

def test_login_unapproved(setup_api):
    resp = requests.post(f"{serverurl}/user/{gtd.fakeusernames['unapproved']}/login", json = {"password": gtd.fakepassword})
    assert_err(resp, errors.NotApproved)

def test_login_nodata(setup_api):
    resp = requests.post(f"{serverurl}/user/{gtd.fakeusernames['buyer']}/login")
    assert resp.status_code == 415 # HTTP Invalid Content Type

def test_login_ok(setup_api):
    resp = requests.post(f"{serverurl}/user/{gtd.fakeusernames['admin']}/login", json = {"password": gtd.fakepassword})
    assert_ok(resp, responses.GenericOK)

def test_login_testing_ok(setup_api):
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    assert isinstance(key, str) == True

def test_logout(setup_api):
    # Login
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)
    resp = requests.get(f"{serverurl}/user/info/{gtd.fakeusernames['seller']}", auth = auth)
    assert_ok(resp, responses.GenericOK)

    # Logout
    resp = requests.get(f"{serverurl}/user/logout", auth = auth)
    assert_ok(resp, responses.GenericOK)

    # Attempt call again
    resp = requests.get(f"{serverurl}/user/info/{gtd.fakeusernames['seller']}", auth = auth)
    assert_err(resp, errors.AuthorizationRequired)

def test_logouteverywhere(setup_api):
    keys = []

    # Login 10 times
    for i in range(0, 10):
        key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
        auth = BearerAuth(key)
        keys.append((key, auth))

    # call user/info with each key twice
    for i in keys:
        for j in range(0, 1):
            resp = requests.get(f"{serverurl}/user/info", auth = i[1])
            assert resp.status_code == 200
            assert resp.json()["users"][0]["username"] == gtd.fakeusernames["admin"]

    # Logout everywhere
    resp = requests.get(f"{serverurl}/user/logouteverywhere", auth = keys[-1][1])
    assert_ok(resp, responses.GenericOK)

    # call user/info again
    for i in keys:
        resp = requests.get(f"{serverurl}/user/info", auth = i[1])
        assert_err(resp, errors.AuthorizationRequired)


#### User Tests ####
## User Info ##
def test_self_user_info(setup_api):
    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)
    resp = requests.get(f"{serverurl}/user/info", auth = auth)
    assert resp.status_code == 200
    assert resp.json()["users"][0]["username"] == gtd.fakeusernames["buyer"]

def test_other_user_info_noperm(setup_api):
    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)
    resp = requests.get(f"{serverurl}/user/info/{gtd.fakeusernames["seller"]}", auth = auth)
    assert_err(resp, errors.ResourceNotFound)

def test_other_user_info_nonexistant(setup_api):
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)
    resp = requests.get(f"{serverurl}/user/info/ObvIouslYFAkEUserNameThAtDoeSNoTExIsT", auth = auth)
    assert_err(resp, errors.ResourceNotFound)

def test_other_user_info_ok(setup_api):
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)
    resp = requests.get(f"{serverurl}/user/info/{gtd.fakeusernames['seller']}", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert resp.json()["users"][0]["username"] == gtd.fakeusernames["seller"]

def test_self_user_info_noauth(setup_api):
    resp = requests.get(f"{serverurl}/user/info")
    assert_err(resp, errors.AuthorizationRequired)

## Approval ##
def test_approve_unapprove(setup_api):
    # Login as admin
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Approve unapproved user
    resp = requests.get(f"{serverurl}/user/{gtd.fakeusernames['unapproved']}/approve", auth = auth)
    assert_ok(resp, responses.GenericOK)
    
    # Attempt login as that user
    unkey = login(gtd.fakeusernames["unapproved"], gtd.fakepassword)
    unauth = BearerAuth(unkey)
    assert isinstance(unkey, str) == True

    # Unapprove user to restore state
    resp = requests.get(f"{serverurl}/user/{gtd.fakeusernames['unapproved']}/unapprove", auth = auth)
    assert_ok(resp, responses.GenericOK)

def test_approve_alreadyapproved(setup_api):
    # Login as admin
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Approve already approved user
    resp = requests.get(f"{serverurl}/user/{gtd.fakeusernames['seller']}/approve", auth = auth)
    assert_err(resp, errors.ResourceAlreadyApproved)

def test_unapproved_alreadynotapproved(setup_api):
    # Login as admin
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Unapprove already non approved user
    resp = requests.get(f"{serverurl}/user/{gtd.fakeusernames['unapproved']}/unapprove", auth = auth)
    assert_err(resp, errors.NotApproved)

def test_approval_noperm(setup_api):
    # Login
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Approve
    resp = requests.get(f"{serverurl}/user/{gtd.fakeusernames['unapproved']}/approve", auth = auth)
    assert_err(resp, errors.AuthorizationRequired)

def test_unapproval_noperm(setup_api):
    # Login
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Unapprove
    resp = requests.get(f"{serverurl}/user/{gtd.fakeusernames['admin']}/unapprove", auth = auth)
    assert_err(resp, errors.AuthorizationRequired)

## Modification ##
def test_modify_ownuser(setup_api):
    testemail = "modtestingemail@email.eml"

    # Login
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Modify user
    resp = requests.patch(f"{serverurl}/user/modify", auth = auth, json = {"email": testemail})
    assert_ok(resp, responses.GenericOK)

    # Get user and check
    resp = requests.get(f"{serverurl}/user/info", auth = auth)
    assert resp.status_code == 200
    assert resp.json()["users"][0]["email"] == testemail

    # Restore
    resp = requests.patch(f"{serverurl}/user/modify", auth = auth, json = {"email": gtd.fakeemails["seller"]})
    assert_ok(resp, responses.GenericOK)

def test_modify_ownuser_noauth(setup_api):
    testemail = "modtestingemail@email.eml"

    # Modify user
    resp = requests.patch(f"{serverurl}/user/modify", json = {"email": testemail})
    assert_err(resp, errors.AuthorizationRequired)

def test_modify_otheruser(setup_api):
    testemail = "modtestingemail@email.eml"

    # Login
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Modify user
    resp = requests.patch(f"{serverurl}/user/modify/{gtd.fakeusernames['buyer']}", auth = auth, json = {"email": testemail})
    assert_ok(resp, responses.GenericOK)

    # Get user and check
    resp = requests.get(f"{serverurl}/user/info/{gtd.fakeusernames['buyer']}", auth = auth)
    assert resp.status_code == 200
    assert resp.json()["users"][0]["email"] == testemail

    # Restore
    resp = requests.patch(f"{serverurl}/user/modify/{gtd.fakeusernames['buyer']}", auth = auth, json = {"email": gtd.fakeemails["buyer"]})
    assert_ok(resp, responses.GenericOK)

def test_modify_otheruser_noexist(setup_api):
    testemail = "modtestingemail@email.eml"

    # Login
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Modify user
    resp = requests.patch(f"{serverurl}/user/modify/ThisUsErDoESNoTExIsT", auth = auth, json = {"email": testemail})
    assert_err(resp, errors.ResourceNotFound)

def test_modify_otheruser_noperm(setup_api):
    testemail = "modtestingemail@email.eml"

    # Login
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Modify user
    resp = requests.patch(f"{serverurl}/user/modify/{gtd.fakeusernames['buyer']}", auth = auth, json = {"email": testemail})
    assert_err(resp, errors.ResourceNotFound)

## Creation ##
def test_createuser(setup_api):
    # Login to test if the user is created
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create user
    resp = requests.post(f"{serverurl}/user/newuser1234/create",
    json = {
        "email": "createtestingemail@email.eml",
        "password": "pa$$WoRd!@#$1234",
        "userlevel": 1 # Admin
    })
    assert_ok(resp, responses.GenericOK)

    # Check for user
    resp = requests.get(f"{serverurl}/user/info/newuser1234", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert resp.json()["users"][0]["username"] == "newuser1234"
    assert resp.json()["users"][0]["approval"] == 0 # New users have to be approved

def test_createuser_missingdata(setup_api):
    # Login to test if the user is created
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create user
    resp = requests.post(f"{serverurl}/user/newuser4321/create",
    # Left password out on purpose
    json = {
        "email": "createtestingemail@email.eml",
        "userlevel": 1 # Admin
    })
    assert_err(resp, errors.MissingArgument)

    # Check for user not existing
    resp = requests.get(f"{serverurl}/user/info/newuser4321", auth = auth)
    assert_err(resp, errors.ResourceNotFound)

def test_createuser_nodata(setup_api):
    # Login to test if the user is created
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create user
    # This is a special case as normally we wouldn't have NO data yet the Content-Type being correct
    resp = requests.post(f"{serverurl}/user/newuser0987/create", headers = {"Content-Type": "application/json"})
    assert_err(resp, errors.InvalidRequest)

    # Check for user not existing
    resp = requests.get(f"{serverurl}/user/info/newuser0987", auth = auth)
    assert_err(resp, errors.ResourceNotFound)

def test_createuser_invalid_userlevel(setup_api):
    # Login to test if the user is created
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create user
    resp = requests.post(f"{serverurl}/user/newuser6543/create",
    json = {
        "email": "createtestingemail@email.eml",
        "password": "pa$$WoRd!@#$1234",
        "userlevel": 12345678910 # Admin
    })
    assert_err(resp, errors.InvalidRequest)

    # Check for user
    resp = requests.get(f"{serverurl}/user/info/newuser6432", auth = auth)
    assert_err(resp, errors.ResourceNotFound)

def test_createuser_already_exists(setup_api):
    # Create user
    resp = requests.post(f"{serverurl}/user/{gtd.fakeusernames['admin']}/create",
    json = {
        "email": "createtestingemail@email.eml",
        "password": "pa$$WoRd!@#$1234",
        "userlevel": 1 # Admin
    })
    assert_err(resp, errors.AlreadyExists)

## User Listing ##
def test_listusers_ok(setup_api):
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # List users
    resp = requests.get(f"{serverurl}/user/list", auth = auth)
    assert_ok(resp, responses.GenericOK)

    # We should have more than 0 users seeing as we at least have the four testing users
    assert len(resp.json()["users"]) > 0

def test_listusers_noperm(setup_api):
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # List users
    resp = requests.get(f"{serverurl}/user/list", auth = auth)
    assert_err(resp, errors.AuthorizationRequired)

#### Items ####
## Listing ##
def test_item_list_ok(setup_api):
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Get items
    resp = requests.get(f"{serverurl}/item/list", auth = auth)
    assert_ok(resp, responses.GenericOK)

def test_item_list_noauth(setup_api):
    # Get items
    resp = requests.get(f"{serverurl}/item/list")
    assert_err(resp, errors.AuthorizationRequired)

## Adding ##
def test_item_add_ok(setup_api):
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Add item
    resp = requests.post(f"{serverurl}/item/add", json = {
        "name": "Test Item",
        "description": """Here are some detailed details about this cool item.\nThis item is used
        purely for testing the API. Please do NOT actually buy this, you will get an empty box.""",
        "quantity": 1776
    }, auth = auth)
    assert_ok(resp, responses.GenericOK)

def test_item_add_noperm(setup_api):
    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Add item
    resp = requests.post(f"{serverurl}/item/add", json = {
        "name": "Test Item",
        "description": """Here are some detailed details about this cool item.\nThis item is used
        purely for testing the API. Please do NOT actually buy this, you will get an empty box.""",
        "quantity": 1776
    })
    assert_err(resp, errors.AuthorizationRequired)

def test_item_add_missingdata(setup_api):
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Add item
    resp = requests.post(f"{serverurl}/item/add", json = {
        "description": """Here are some detailed details about this cool item.\nThis item is used
        purely for testing the API. Please do NOT actually buy this, you will get an empty box.""",
        "quantity": 1776
    }, auth = auth)
    assert_err(resp, errors.MissingArgument)

def test_item_add_baddata(setup_api):
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Add item
    resp = requests.post(f"{serverurl}/item/add", json = {
        "name": "Test Item",
        "description": """Here are some detailed details about this cool item.\nThis item is used
        purely for testing the API. Please do NOT actually buy this, you will get an empty box.""",
        "quantity": "not an integer"
    }, auth = auth)
    assert_err(resp, errors.InvalidRequest)

def test_item_add_nodata(setup_api):
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Add item
    #T his is a special case as normally we wouldn't have NO data yet the Content-Type being correct
    resp = requests.post(f"{serverurl}/item/add", headers = {"Content-Type": "application/json"}, auth = auth)
    assert_err(resp, errors.InvalidRequest)

def test_item_add_otheruser(setup_api):
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Get user
    resp = requests.get(f"{serverurl}/user/info/{gtd.fakeusernames['seller']}", auth = auth)
    assert_ok(resp, responses.GenericOK)
    seller = resp.json()["users"][0]

    # Add item
    resp = requests.post(f"{serverurl}/item/add", json = {
        "name": "Test Item",
        "description": """Here are some detailed details about this cool item.\nThis item is used
        purely for testing the API. Please do NOT actually buy this, you will get an empty box.""",
        "quantity": 1776,
        "seller": seller["id"]
    }, auth = auth)
    assert_ok(resp, responses.GenericOK)

def test_item_add_otheruser_noperm(setup_api):
    key = login(gtd.fakeusernames["seller"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Add item
    resp = requests.post(f"{serverurl}/item/add", json = {
        "name": "Test Item",
        "description": """Here are some detailed details about this cool item.\nThis item is used
        purely for testing the API. Please do NOT actually buy this, you will get an empty box.""",
        "quantity": 1776,
        "seller": "769efb72672b4e9d820726a87a681fb0" # ID generated with uuid.uuid4().hex just like it is otherwise
    }, auth = auth)
    assert_ok(resp, responses.GenericOK)

#### Orders ####
## Creation ##
def test_create_order_ok(setup_api):
    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create order
    resp = requests.post(f"{serverurl}/order/create", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert resp.json()["username"] == gtd.fakeusernames["buyer"]

def test_create_order_noauth(setup_api):
    # Create order
    resp = requests.post(f"{serverurl}/order/create")
    assert_err(resp, errors.AuthorizationRequired)

## Deletion ##
def test_delete_order_ok(setup_api):
    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create order
    resp = requests.post(f"{serverurl}/order/create", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert resp.json()["username"] == gtd.fakeusernames["buyer"]
    orderid = resp.json()["id"]

    # Delete order
    resp = requests.delete(f"{serverurl}/order/{orderid}/delete", auth = auth)
    assert_ok(resp, responses.GenericOK)

def test_delete_order_noperm(setup_api):
    key = login(gtd.fakeusernames["admin"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create order
    resp = requests.post(f"{serverurl}/order/create", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert resp.json()["username"] == gtd.fakeusernames["admin"]
    orderid = resp.json()["id"]

    nonkey = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    nonauth = BearerAuth(nonkey)

    # Delete order
    resp = requests.delete(f"{serverurl}/order/{orderid}/delete", auth = nonauth)
    assert_err(resp, errors.ResourceNotFound)

def test_delete_order_noexist(setup_api):
    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Delete order
    resp = requests.delete(f"{serverurl}/order/NaNaNaNaNaNaNaNaNaNaNaNa/delete", auth = auth)
    assert_err(resp, errors.ResourceNotFound)

## Item Management ##
# Adding #
def test_order_item_add(setup_api):
    testquantity = 5

    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create order to add items too
    resp = requests.post(f"{serverurl}/order/create", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert resp.json()["username"] == gtd.fakeusernames["buyer"]
    orderid = resp.json()["id"]

    # Make sure order has 0 items
    resp = requests.get(f"{serverurl}/order/{orderid}/info", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert len(resp.json()["items"]) == 0 # New order should have 0 items
 
    # Grab item to add
    resp = requests.get(f"{serverurl}/item/list/{gtd.fakeusernames['seller']}", auth = auth)
    assert_ok(resp, responses.GenericOK)
    item = resp.json()["items"][0]

    # Add item
    resp = requests.post(f"{serverurl}/order/{orderid}/add/{item['id']}/{testquantity}", auth = auth)
    assert_ok(resp, responses.GenericOK)

    # Make sure order has the right amount of the right items
    resp = requests.get(f"{serverurl}/order/{orderid}/info", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert len(resp.json()["items"]) == 1 # We only added 1 items
    assert resp.json()["items"][0]["id"] == item["id"]
    assert resp.json()["items"][0]["quantity"] == testquantity

def test_order_item_add_invalidorder(setup_api):
    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Grab item to add
    resp = requests.get(f"{serverurl}/item/list/{gtd.fakeusernames['seller']}", auth = auth)
    assert_ok(resp, responses.GenericOK)
    item = resp.json()["items"][0]

    # Add item
    resp = requests.post(f"{serverurl}/order/NaNaNaNaNaNaNaNaNaNaNaNaN/add/{item['id']}/5", auth = auth)
    assert_err(resp, errors.ResourceNotFound)

def test_order_item_add_invaliditem(setup_api):
    testquantity = 5

    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create order to add items too
    resp = requests.post(f"{serverurl}/order/create", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert resp.json()["username"] == gtd.fakeusernames["buyer"]
    orderid = resp.json()["id"]

    # Make sure order has 0 items
    resp = requests.get(f"{serverurl}/order/{orderid}/info", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert len(resp.json()["items"]) == 0 # New order should have 0 items
 
    # Add item
    resp = requests.post(f"{serverurl}/order/{orderid}/add/NaNaNaNaNaNaNaNaNaNaNaNaN/{testquantity}", auth = auth)
    assert_err(resp, errors.ResourceNotFound)

def test_order_item_add_invalidquantity(setup_api):
    testquantity = -1

    key = login(gtd.fakeusernames["buyer"], gtd.fakepassword)
    auth = BearerAuth(key)

    # Create order to add items too
    resp = requests.post(f"{serverurl}/order/create", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert resp.json()["username"] == gtd.fakeusernames["buyer"]
    orderid = resp.json()["id"]

    # Make sure order has 0 items
    resp = requests.get(f"{serverurl}/order/{orderid}/info", auth = auth)
    assert_ok(resp, responses.GenericOK)
    assert len(resp.json()["items"]) == 0 # New order should have 0 items
 
    # Grab item to add
    resp = requests.get(f"{serverurl}/item/list/{gtd.fakeusernames['seller']}", auth = auth)
    assert_ok(resp, responses.GenericOK)
    item = resp.json()["items"][0]

    # Add item
    resp = requests.post(f"{serverurl}/order/{orderid}/add/{item['id']}/{testquantity}", auth = auth)
    assert resp.status_code == 404

# Deleting