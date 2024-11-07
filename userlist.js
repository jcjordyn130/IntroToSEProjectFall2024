const relativeUrl = "/user/list";
var userListElement = document.getElementById("user-list");

if (userListElement) {
    try {
        const apiResponse = await fetch(relativeUrl);
        if (!apiResponse.ok) {
            throw new Error(`${relativeUrl} returned status ${apiResponse.status}`);
        }
        // =====
        userListText = "";
        for (let user of apiResponse) {
            userListText += `<h1>User <i>${user.username}</i></h1>\n`;
            userListText += "<ul>\n";
            userListText += `<li>ID: ${user.id}</li>\n`;
            userListText += `<li>Email: ${user.email}</li>\n`;
            userListText += `<li>Level: ${user.userlevel}</li>\n`;
            userListText += "</ul>\n\n";
            // TODO: Add functionality to approve and unapprove.
        }
        userListElement.innerText = userListText;
    }
    catch (e) {
        console.error(e.message);
    }
}
