$(document).ready(function () {
    $("#create-acc-submit").click(function () {
        const fd = new FormData(document.getElementById("create-form"));
        const fdUsername = fd.get("username");
        const fdPassword = fd.get("password");
        const fdEmailAddress = fd.get("email-address");
        const fdUserLevel = fd.get("user-level");
        $.ajax({
            type: "POST",
            url: "http://dankpadserver.jordynsblog.org:5000/user/" + fdUsername + "/create",
            contentType: "application/json",
            data: {
                email: fdEmailAddress,
                password: fdPassword,
                userlevel: fdUserLevel
            },
            success: function () {
                document.getElementById("create-form-div").style.display = "none";
            }
        });
    });
});

/*
function FormCreate() {
    const fd = new FormData(document.getElementById("create-form"));
    const fdUsername = fd.get("username");
    const fdPassword = fd.get("password");
    const fdEmailAddress = fd.get("email-address");
    const fdUserLevel = fd.get("user-level");
    const options = {
        headers: { "Content-Type": "application/json; charset=utf-8" },
        mode: "no-cors",
        method: "POST",
        body: JSON.stringify({
            email: fdEmailAddress,
            password: fdPassword,
            userlevel: fdUserLevel
        })
    };

    // Put jquery post function here.
    $.post(absoluteUrl + "user/" + fdUsername + "/create", FormCreateSuccess())
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
*/