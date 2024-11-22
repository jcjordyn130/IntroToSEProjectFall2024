$(document).ready(function () {
    const userListElement = document.getElementById("user-list");
    if (userListElement) {
        $.ajax({
            type: "GET",
            url: "http://dankpadserver.jordynsblog.org:5000/user/list",
            data: JSON.stringify({
                apikey: localStorage.getItem("apikey") // Is this correct?
            }),
            dataType: "json",
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
                    userListText += `<a href="user.html?${userParams.toString()}"></a>`
                }
                userListElement.innerHTML = userListText;
            }
        });
    }
});

/*
const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000";
//const absoluteUrl = ".";
var userListElement = document.getElementById("user-list");
if (userListElement) {
    fetch(absoluteUrl + "/user/list")
        .then(
            response => {
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
                    userListText += `<a href="user.html?${userParams.toString()}"></a>`
                }
                userListElement.innerHTML = userListText;
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}
*/