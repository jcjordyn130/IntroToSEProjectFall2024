const relativeUrl = "/user/list";
var userListElement = document.getElementById("user-list");

if (userListElement) {
    try {
        const apiResponse = fetch(relativeUrl); // removed `await`
        if (!apiResponse.ok) {
            throw new Error(`${relativeUrl} returned status ${apiResponse.status}`);
        }
        // =====
        var userListText = "";
        for (let user of apiResponse) {
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
    catch (e) {
        console.error(e.message);
    }
}
