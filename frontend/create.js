$(document).ready(function () {
    $("#create-acc-submit").click(function () {
        const fd = new FormData(document.getElementById("create-form"));
        const fdUsername = fd.get("username");
        const fdPassword = fd.get("password");
        const fdEmailAddress = fd.get("email");
        const fdUserType = fd.get("user-type");
        var fdUserLevel = 3;
        switch (fdUserType) {
            case "admin":
                fdUserLevel = 1;
                break;
            case "seller":
                fdUserLevel = 2;
                break;
            default:
                break;
        }
        $.ajax(
            {
                type: "POST",
                url: "http://dankpadserver.jordynsblog.org:5000/user/" + fdUsername + "/create",
                contentType: "application/json",
                data:
                JSON.stringify({
                    email: fdEmailAddress,
                    password: fdPassword,
                    userlevel: fdUserLevel
                }),
                dataType: "json",
                processData: false,
                success: function () {
                    document.getElementById("create-form-div").style.display = "none";
                }
            });
    });
});

/*function validateForm() // adding the "required" tag to the elements made this function redundant
{
    let x = document.forms["create-form"]["username-input"].value;
    if (x == "")
    {
        alert("Username must be filled out");
        return false;
    }
}*/

// This function needs to call the api to make a new account with the information from the form
function submit_form() {
    //let username = document.forms["create-form"]["username"].value;
    //let password = document.forms["create-form"]["password"].value;
    //let email = document.forms["create-form"]["email"].value;
    //let user_type = document.forms["create-form"]["user-type"].value;
    alert("Hello World");
    return;
}

//submit_form();

/*
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
*/