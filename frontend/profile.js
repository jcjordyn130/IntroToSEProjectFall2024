var username = null;
for (const [k, v] of URLSearchParams()) {
    if (k == "username")
        username = v;
} // get username from the URL

var usernameElement = null;
usernameElement = document.getElementById("username");

var apiIdElement = null;
apiIdElement = document.getElementById("api-id");

var emailElement = null;
emailElement = document.getElementById("email");

var userLevelElement = null;
userLevelElement = document.getElementById("user-level");

var approvedElement = null;
approvedElement = document.getElementById("approved"); // initializing HTML elements

if (username) {
    try {
        const relativeUrl = "user/info/" + username;
        const apiResponse = fetch(relativeUrl);
        if (!apiResponse.ok)
            throw new Error(`${relativeUrl} returned status ${apiResponse.status}`);
        let data = apiResponse.json;
        if (usernameElement)
            usernameElement.innerHTML = data.username;
        if (apiIdElement)
            apiIdElement.innerHTML = `ID: ${data.id}`;
        if (emailElement)
            emailElement.innerHTML = `Email: ${data.email}`;
        if (userLevelElement)
            userLevelElement.innerHTML = `User Level: ${data.userlevel}`;
        if (approvedElement)
            approvedElement.innerHTML = `Approved: ${data.approval}`;
    }
    catch (e) {
        console.error(e.message);
    }
}