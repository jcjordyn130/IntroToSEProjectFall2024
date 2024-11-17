const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000/";
//const absoluteUrl = "./";

function FormCreate() {
    const fd = FormData(document.getElementById("create-form"));
    const fdUsername = fd.get("username");
    const fdPassword = fd.get("password");
    const fdEmailAddress = fd.get("email-address");
    const fdUserLevel = fd.get("user-level");
    fetch(absoluteUrl + "user/" + fdUsername + "/create", {
        method: "POST",
        body: JSON.stringify({
            email: fdEmailAddress,
            password: fdPassword,
            userlevel: fdUserLevel
        })
    })
    .then(
        response => {
            document.getElementById("create-form-div").style.display = "none";
        }
    ).catch(
        (e) => {
            console.error(e.message);
        }
    );
}

FormCreate();