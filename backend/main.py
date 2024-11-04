from flask import Flask

app = Flask("api/api.py")
app.debug = True

if __name__ == "__main__":
	app.run(host = "127.0.0.1", port = "5000", debug = app.debug)
