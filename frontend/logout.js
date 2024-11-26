$(document).ready(function () {
    $("#logout-link").click(function () {
        $.ajax({
            url: "http://dankpadserver.jordynsblog.org:5000/user/logout",
            data: new URLSearchParams({
                key: localStorage.getItem("apikey") // Is this correct?
            }).toString(),
            success: revertLoginForm()
        });
    });
    $("#logout-e-link").click(function () {
        $.ajax({
            url: "http://dankpadserver.jordynsblog.org:5000/user/logouteverywhere",
            data: new URLSearchParams({
                key: localStorage.getItem("apikey") // Is this correct?
            }).toString(),
            success: revertLoginForm()
        });
    });
});

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
    localStorage.removeItem("apikey");
}
