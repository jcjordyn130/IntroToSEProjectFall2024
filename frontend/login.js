import("https://code.jquery.com/jquery-3.7.1.min.js");

$(document).ready(function () {
    $("#login-form-link").click(function () {
        const fd = new FormData(document.getElementById("login-form"));
        const fdUsername = fd.get("username");
        console.log(fdUsername);
        const fddiv = document.getElementById("login-form-div");
        const logoutdiv = document.getElementById("logout-form-div");
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                password: fd.get("password")
            }),
            dataType: "json",
            url: "http://dankpadserver.jordynsblog.org:5000/user/" + fdUsername.toString() + "/login",
            success: function (response) {
                if (fddiv.style.display == "block") {
                    document.getElementById("login-form-div").style.display = "none";
                }
                if (logoutdiv) {
                    logoutdiv.style.display = "block";
                    document.getElementById("login-message").innerText = `You're logged in as ${fdUsername}.`;
                    document.getElementById("login-message").innerText += `\nAPI Key: ${response.apikey}`;
                }
                localStorage.setItem("username", fdUsername);
                localStorage.setItem("password", fd.get("password"));
                localStorage.setItem("apikey", response.apikey);
            }
        });
    });
});