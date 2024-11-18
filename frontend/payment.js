const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000/";
//const absoluteUrl = "./";

function CreatePaymentMethod() {
    const fd = FormData(document.getElementById("payment-create-form"));
    fetch(absoluteUrl + "payment/" + fd.get("methodname") + "/create", {
        cardno: fd.get("cardno"),
        cardexp: fd.get("cardexp"),
        cardcvv: fd.get("cardcvv"),
        billingaddress: fd.get("billingaddress")
    })
        .then(
            response => {
                document.getElementById("payment-create-form").reset();
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

function RemovePaymentMethod(id) {
    fetch(absoluteUrl + "payment/" + id + "/remove")
        .then(
            response => {
                const buttonElement = document.getElementById("remove-" + id);
                if (buttonElement) {
                    buttonElement.innerText = "Method Removed";
                    buttonElement.onclick = `console.log("Payment Method Already Removed!")`;
                }
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

function GeneratePaymentMethods() {
    const paymentElement = document.getElementById("payment-info-div");
    const createElement = document.getElementById("payment-create-div");
    if (!paymentElement || !createElement)
        return;
    fetch(absoluteUrl + "payment/list")
        .then(
            response => {
                var paymentText = "";
                let data = response.json().paymentmethods;
                for (let pm of data) {
                    paymentText += "<ul>\n";
                    paymentText += `<li>Name: ${pm.name}</li>\n`
                    paymentText += `<li>ID: ${pm.id}</li>\n`
                    paymentText += "</ul>\n";
                    paymentText += `<button type="button" id="remove-${pm.id}" onclick="RemovePaymentMethod(${pm.id})">Remove</button>\n`;
                    paymentText += "<br/>\n"
                }
                document.getElementById("payment-info-div").innerHTML = paymentText;
                const authMsgElement = document.getElementById("auth-message");
                if (authMsgElement)
                    authMsgElement.style.display = "none";
                paymentElement.style.display = "block";
                createElement.style.display = "block";
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

GeneratePaymentMethods();