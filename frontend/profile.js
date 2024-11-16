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
    const apiResponse = fetch("user/info/" + username).then(
        response => {
            let data = response.json();
            if (usernameElement)
                usernameElement.innerText = data.username;
            if (apiIdElement)
                apiIdElement.innerText = `ID: ${data.id}`;
            if (emailElement)
                emailElement.innerText = `Email: ${data.email}`;
            if (userLevelElement)
                userLevelElement.innerText = `User Level: ${data.userlevel}`;
            if (approvedElement)
                approvedElement.innerText = `Approved: ${data.approval}`;
        }
    )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}