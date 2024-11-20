//const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000/";
//const absoluteUrl = "./";

function revertLoginForm() {
    const logindiv = document.getElementById("login-form-div");
    const logoutdiv = document.getElementById("logout-form-div");
    const logoutmsg = document.getElementById("login-message");
    if (logindiv) {
        document.getElementById("login-form-div").style.display = "block";
    }
    if (logoutdiv) {
        document.getElementById("logout-form-div").style.display = "none";
    }
    if (logoutmsg) {
        document.getElementById("login-message").innerText = "Not Logged In!";
    }
}

function Logout() {
    fetch( "http://dankpadserver.jordynsblog.org:5000/" + "user/logout")
        .then(
            response => {
                revertLoginForm();
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

function LogoutE() {
    fetch("http://dankpadserver.jordynsblog.org:5000/" + "user/logouteverywhere")
        .then(
            response => {
                revertLoginForm();
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}