var username = null;
for (const [k, v] of URLSearchParams()) {
    if (k == "username")
        username = v;
} // get username from the URL

var usernameElement = null;
usernameElement = document.getElementById("username");

var userInfoElement = document.getElementById("userinfo");

var buttonElement1 = null;
buttonElement1 = document.getElementById("button1"); // approve
var buttonElement2 = null;
buttonElement2 = document.getElementById("button2"); // unapprove

function userAlreadyApproved() {
    console.log("User Already Approved or Unapproved.");
}

function approveUser() {
    if (username && userInfoElement) {
        try {
            approveUrl = "/user/" + username + "/approve"
            approveResponse = fetch(approveUrl);
            if (!approveResponse.ok) {
                buttonElement1.innerText = "Error";
                throw new Error(`${approveUrl} returned status ${approveResponse.status}`);
            }
            buttonElement1.onclick = "userAlreadyApproved()";
            buttonElement1.innerText = "User Approved";
            buttonElement2.style.display = "none";
        }
        catch (e) {
            console.error(e.message);
        }
    }
}

function unapproveUser() {
    if (username && userInfoElement && buttonElement2) {
        try {
            unapproveUrl = "/user/" + username + "/unapprove"
            unapproveResponse = fetch(approveUrl);
            if (!unapproveResponse.ok) {
                buttonElement2.innerText = "Error";
                throw new Error(`${unapproveUrl} returned status ${unapproveResponse.status}`);
            }
            buttonElement2.onclick = "userAlreadyApproved()";
            buttonElement1.style.display = "none";
            buttonElement2.innerText = "User Unapproved"
        }
        catch (e) {
            console.error(e.message);
        }
    }
}

if (username && userInfoElement) {
    if (usernameElement)
        usernameElement.innerText = username;    
    try {
        const relativeUrl = "/user/info/" + username;
        const apiResponse = fetch(relativeUrl);
        if (!apiResponse.ok)
            throw new Error(`${relativeUrl} returned status ${apiResponse.status}`);
        // =====
        let data = apiResponse.json();
        var userInfoText = "<ul>\n";
        userInfoText += `<li>ID: ${data.id}</li>\n`;
        userInfoText += `<li>Email: ${data.email}</li>\n`;
        userInfoText += `<li>Level: ${data.userlevel}</li>\n`;
        userInfoText += "</ul>\n\n";
        userInfoText += `<button id="button1" onclick="approveUser()">Approved?</button>\n`;
        userInfoText += `<button id="button2" onclick="unapproveUser()">Unapproved?</button>\n\n`;
        userInfoElement.innerHTML = userInfoText;
    }
    catch (e) {
        console.error(e.message)
    }
}
