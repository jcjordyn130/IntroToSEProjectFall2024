$(document).ready(function () {
    const fddiv = document.getElementById("login-form-div");
    const logoutdiv = document.getElementById("logout-form-div");
    if (localStorage.username && localStorage.password) {
        const userListElement = document.getElementById("user-list");
        if (userListElement) {
            $.ajax({
                type: "GET",
                url: "http://dankpadserver.jordynsblog.org:5000/user/list",
                headers: {
                    Authorization: "Bearer " + localStorage.getItem("apikey")
                },
                success: function (response) {
                    var userListText = "";
                    for (let user of response.users) {
                        userListText = "<ul>\n";
                        userListText += `<li>ID: ${user.id}</li>\n`;
                        userListText += `<li>Email: ${user.email}</li>\n`;
                        userListText += `<li>Level: ${user.userlevel}</li>\n`;
                        userListText += "</ul>\n\n";
                        // =====
                        const userParams = new URLSearchParams();
                        userParams.append("username", user.username);
                        userListText += `<a href="user.html?${userParams.toString()}">View User</a>`;
                    }
                    userListElement.innerHTML = userListText;
                }
            });
        }
    }
});