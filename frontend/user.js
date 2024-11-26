var username = null;
for (const [k, v] of new URLSearchParams()) {
    if (k == "username")
        username = v;
} // get username from the URL

const usernameElement = document.getElementById("username");
const userInfoElement = document.getElementById("userinfo");
const buttonElement1 = document.getElementById("button1"); // approve
const buttonElement2 = document.getElementById("button2"); // unapprove

function approveUser() {
    if (!username || !userInfoElement)
        return;
    $.ajax({
        type: "GET",
        url: `http://dankpadserver.jordynsblog.org:5000/user/${username}/approve`,
        data: JSON.stringify({
            key: localStorage.getItem("apikey") // Is this correct?
        }),
        dataType: "json",
        success: function () {
            buttonElement1.onclick = `console.log("User Approval Already Set")`;
            buttonElement1.innerText = "User Approved";
            buttonElement2.style.display = "none";
        }
    });
}

function unapproveuser() {
    if (!username || !userInfoElement)
        return;
    $.ajax({
        type: "GET",
        url: `http://dankpadserver.jordynsblog.org:5000/user/${username}/unapprove`,
        data: JSON.stringify({
            key: localStorage.getItem("apikey") // Is this correct?
        }),
        dataType: "json",
        success: function () {
            buttonElement1.style.display = "none";
            buttonElement2.onclick = `console.log("User Approval Already Set")`;
            buttonElement2.innerText = "User Unapproved"
        }
    });
}

$(document).ready(function () {
    if (!username || !userInfoElement)
        return;
    if (usernameElement)
        usernameElement.innerText = username;
    $.ajax({
        type: "GET",
        url: "http://dankpadserver.jordynsblog.org:5000/user/info/" + username,
        data: JSON.stringify({
            key: localStorage.getItem("apikey") // Is this correct?
        }),
        dataType: "json",
        success: function (response) {
            let data = response.json().users[0]; // one item in list
            var userInfoText = `<li>ID: ${data.id}</li>\n`;
            userInfoText += `<li>Email: ${data.email}</li>\n`;
            userInfoText += `<li>Level: ${data.userlevel}</li>\n`;
            userInfoText = "<ul>\n" + userInfoText + "</ul>\n";
            userInfoText += `<button id="button1" onclick="approveUser()">Approved?</button>\n`;
            userInfoText += `<button id="button2" onclick="unapproveUser()">Unapproved?</button>\n`;
            userInfoElement.innerHTML = userInfoText;
        }
    });
});