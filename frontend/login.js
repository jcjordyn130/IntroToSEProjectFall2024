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
    options = {
        method: "POST",
        headers: { "content-type": "application/json" },
        mode: "no-cors"
    };
    options.body = JSON.stringify({
        password: fd.get("password")
    });
    fetch("http://dankpadserver.jordynsblog.org:5000/user/" + fdUsername + "/login", options)
    .then(response => response.json())
    .then(
        data => {
            if (fddiv.style.display == "block") {
                document.getElementById("login-form-div").style.display = "none";
            }
           if (logoutdiv) {
                logoutdiv.style.display = "block";
                document.getElementById("login-message").innerText = `You're logged in as ${fdUsername}.`;
                document.getElementById("login-message").innerText += `\nAPI Key: ${data.apikey}`
            }
        }
    ).catch((e) => {
        console.error(e.message);
    });
}

const profileInfo = document.getElementById("profileinfo");