const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000";
//const absoluteUrl = ".";

function liElement(inputString) {
    return "<li>" + inputString + "</li>\n";
}

function FormLogin() {
    const fd = FormData(document.getElementById("login-form"))
    var fddiv = document.getElementById("login-form-div");
    fetch(absoulteUrl + "/user/" + fd.get("username") + "/login")
    .then(
        response => {
            if (fddiv.display == "block") {
                document.getElementById("login-form-div").display == "none";
            }
            // include a "logged in as ___" message as well
            profileInfo.innerHTML = liElement("A");
            profileInfo.innerHTML += liElement("B");
            profileInfo.innerHTML += liElement("C");
            profileInfo.innerHTML += liElement("D");
            profileInfo.innerHTML += liElement("E");
        }
    ).catch((e) => {
        console.error(e.message);
    })
}

const profileInfo = document.getElementById("profileinfo");



FormLogin();