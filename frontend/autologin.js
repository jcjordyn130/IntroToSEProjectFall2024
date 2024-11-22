$(document).ready(function () {
  if (localStorage.username && localStorage.password) {
    console.log("API Key: " + localStorage.getItem("apikey") + "\n");
    const lsUsername = localStorage.getItem("username");
    const lsPassword = localStorage.getItem("password");
    $.ajax({
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        password: lsPassword
      }),
      dataType: "json",
      url: "http://dankpadserver.jordynsblog.org:5000/user/" + lsUsername.toString() + "/login",
      success: function (response) {
        let data = response.json();
        if (fddiv.style.display == "block") {
          document.getElementById("login-form-div").style.display = "none";
        }
        if (logoutdiv) {
          logoutdiv.style.display = "block";
          document.getElementById("login-message").innerText = `You're logged in as ${lsUsername}.`;
          document.getElementById("login-message").innerText += `\nAPI Key: ${data.apikey}`;
        }
        localStorage.setItem("username", lsUsername);
        localStorage.setItem("password", lsPassword); // are these first two necessary?
        localStorage.setItem("apikey", data.apikey);
      }
    });
  }
});