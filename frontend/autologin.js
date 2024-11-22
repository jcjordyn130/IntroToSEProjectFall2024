$(document).ready(function () {
    if (localStorage.apikey) {
      console.log("API Key: " + localStorage.getItem("apikey") + "\n"); // Put auto-login here
    }
  });