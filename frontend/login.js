//const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000/";
//const absoluteUrl = "./";

function liElement(inputString) {
    return "<li>" + inputString + "</li>\n";
}

function FormLogin() {
    const fd = new FormData(document.getElementById("login-form"));
    const fdUsername = fd.get("username");
    var fddiv = document.getElementById("login-form-div");
    const logoutdiv = document.getElementById("logout-form-div");
    fetch("http://dankpadserver.jordynsblog.org:5000/user/" + fdUsername + "/login")
    .then(
        response => {
            if (fddiv.style.display == "block") {
                document.getElementById("login-form-div").style.display = "none";
            }
           if (logoutdiv) {
                logoutdiv.style.display = "block";
                document.getElementById("login-message").innerText = `Logged in as ${fdUsername}`;
            }
        }
    ).catch((e) => {
        console.error(e.message);
    });
}

const profileInfo = document.getElementById("profileinfo");