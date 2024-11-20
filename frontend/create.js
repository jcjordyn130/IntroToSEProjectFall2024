const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000/";
//const absoluteUrl = "./";

function FormCreate() {
    const fd = new FormData(document.getElementById("create-form"));
    const fdUsername = fd.get("username");
    const fdPassword = fd.get("password");
    const fdEmailAddress = fd.get("email-address");
    const fdUserLevel = fd.get("user-level");
    const options = {
        method: "POST",
        headers: { "content-type": "application/json" },
        mode: "no-cors"
    };
    options.body = JSON.stringify({
        email: fdEmailAddress,
        password: fdPassword,
        userlevel: fdUserLevel
    });

    fetch(absoluteUrl + "user/" + fdUsername + "/create", options)
        .then(
            response => {
                if (response.ok) {
                    document.getElementById("create-form-div").style.display = "none";
                }
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}