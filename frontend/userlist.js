$(document).ready(function () {
    const fddiv = document.getElementById("login-form-div");
    const logoutdiv = document.getElementById("logout-form-div");
    if (localStorage.username && localStorage.password) {
        const userListElement = document.getElementById("user-list");
        const keyFromURL = localStorage.getItem("apikey");
        for ([k, v] of new URLSearchParams())
            if (k == "key")
                keyFromURL = v;
        if (userListElement) {
            $.ajax({
                type: "GET",
                url: "http://dankpadserver.jordynsblog.org:5000/user/list",
                data: new URLSearchParams({
                    key: keyFromURL
                }).toString(),
                success: function (response) {
                    var userListText = "";
                    let data = response.json().users;
                    for (let user of data) {
                        userListText = "<ul>\n";
                        userListText += `<li>ID: ${user.id}</li>\n`;
                        userListText += `<li>Email: ${user.email}</li>\n`;
                        userListText += `<li>Level: ${user.userlevel}</li>\n`;
                        userListText += "</ul>\n\n";
                        // =====
                        const userParams = new URLSearchParams();
                        userParams.append("username", user.username);
                        userListText += `<a href="user.html?${userParams.toString()}"></a>`;
                    }
                    userListElement.innerHTML = userListText;
                }
            });
        }
    }
});