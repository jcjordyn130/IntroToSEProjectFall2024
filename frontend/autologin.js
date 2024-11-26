import("https://code.jquery.com/jquery-3.7.1.min.js");

function autoLogin() {
  const fddiv = document.getElementById("login-form-div");
  const logoutdiv = document.getElementById("logout-form-div");
  if (localStorage.username && localStorage.password) {
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
        if (fddiv.style.display == "block") {
          document.getElementById("login-form-div").style.display = "none";
        }
        if (logoutdiv) {
          logoutdiv.style.display = "block";
          document.getElementById("login-message").innerText = `You're logged in as ${lsUsername}.`;
          document.getElementById("login-message").innerText += `\nAPI Key: ${response.apikey}`;
        }
        localStorage.setItem("username", lsUsername);
        localStorage.setItem("password", lsPassword); // are these first two necessary?
        localStorage.setItem("apikey", response.apikey);
      }
    });
  }
}