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
                let data = response.json();
                if (fddiv.style.display == "block") {
                    document.getElementById("login-form-div").style.display = "none";
                }
                if (logoutdiv) {
                    logoutdiv.style.display = "block";
                    document.getElementById("login-message").innerText = `You're logged in as ${fdUsername}.`;
                    document.getElementById("login-message").innerText += `\nAPI Key: ${data.apikey}`;
                }
            }
        });
    });
});

/*
function formLogin() {
    const fd = new FormData(document.getElementById("login-form"));
    const fdUsername = fd.get("username");
    const fddiv = document.getElementById("login-form-div");
    const logoutdiv = document.getElementById("logout-form-div");
    $.ajax({
        type: "POST",
        contentType: "application/json",
        data: {
            password: fd.get("password")
        },
        url: `http://dankpadserver.jordynsblog.org:5000/user/${fdUsername}/login`,
        success: function (response) {
            let data = response.json();
            if (fddiv.style.display == "block") {
                document.getElementById("login-form-div").style.display = "none";
            }
            if (logoutdiv) {
                logoutdiv.style.display = "block";
                document.getElementById("login-message").innerText = `You're logged in as ${fdUsername}.`;
                document.getElementById("login-message").innerText += `\nAPI Key: ${data.apikey}`;
            }
        }
    });
}
    */