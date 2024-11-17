const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000/";
//const absoluteUrl = "./";

function liElement(inputString) {
    return "<li>" + inputString + "</li>\n";
}

function FormLogin() {
    const fd = FormData(document.getElementById("login-form"))
    const fdUsername = fd.get("username");
    var fddiv = document.getElementById("login-form-div");
    const logoutdiv = document.getElementById("logout-form-div");
    fetch(absoluteUrl + "user/" + fdUsername + "/login")
    .then(
        response => {
            if (fddiv.display == "block") {
                document.getElementById("login-form-div").display = "none";
            }
           if (logoutdiv) {
                logoutdiv.display = "block";
                document.getElementById("login-message").innerText = `Logged in as ${fdUsername}`;
            }
        }
    ).catch((e) => {
        console.error(e.message);
    })
}

const profileInfo = document.getElementById("profileinfo");



FormLogin();