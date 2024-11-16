function userAlreadyApproved() {
    console.log("User Approval Already Set");
}

function approveUser() {
    if (!username || !userInfoElement)
        return;
    fetch("/user/" + username + "/approve")
        .then(
            response => {
                buttonElement1.onclick = "userAlreadyApproved()";
                buttonElement1.innerText = "User Approved";
                buttonElement2.style.display = "none";
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

function unapproveuser() {
    if (!username || !userInfoElement)
        return;
    fetch("/user/" + username + "/unapprove")
        .then(
            response => {
                buttonElement1.style.display = "none";
                buttonElement2.onclick = "userAlreadyApproved()";
                buttonElement2.innerText = "User Unapproved";
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

function UserApproveForm() {
    if (!username || !userInfoElement)
        return;

    if (usernameElement)
        usernameElement.innerText = username;
    const relativeUrl = "/user/info/" + username;
    const apiResponse = fetch(relativeUrl)
        .then(
            response => {
                let data = response.json();
                var userInfoText = `<li>ID: ${data.id}</li>\n`;
                userInfoText += `<li>Email: ${data.email}</li>\n`;
                userInfoText += `<li>Level: ${data.userlevel}</li>\n`;
                userInfoText = "<ul>\n" + userInfoText + "</ul>\n";
                userInfoText += `<button id="button1" onclick="approveUser()">Approved?</button>\n`;
                userInfoText += `<button id="button2" onclick="unapproveUser()">Unapproved?</button>\n`;
                userInfoElement.innerHTML = userInfoText;
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

var username = null;
for (const [k, v] of URLSearchParams()) {
    if (k == "username")
        username = v;
} // get username from the URL

const usernameElement = document.getElementById("username");
const userInfoElement = document.getElementById("userinfo");
const buttonElement1 = document.getElementById("button1"); // approve
const buttonElement2 = document.getElementById("button2"); // unapprove

UserApproveForm();
