const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000/";
//const absoluteUrl = "./";

function approveItem(id) {
    fetch(absoluteUrl + `item/${id}/unapprove`)
    .then(
        response => {
            document.getElementById("button2-" + id).style.display = "none";
            document.getElementById("button1-" + id).onclick = `console.log("Item Already Approved!")`;
            document.getElementById("button1-" + id).innerText = "Item Approved";
        }
    )
    .catch(
        (e) => {
            console.error(e.message);
        }
    );
}

function unapproveItem(id) {
    fetch(absoluteUrl + `item/${id}/approve`)
    .then(
        response => {
            document.getElementById("button1-" + id).style.display = "none";
            document.getElementById("button2-" + id).onclick = `console.log("Item Already Unapproved!")`;
            document.getElementById("button2-" + id).innerText = "Item Unapproved";
        }
    ).catch(
        (e) => {
            console.error(e.message);
        }
    );
}

function GenerateItemList() {
    const itemListElement = document.getElementById("item-list");
    if (!itemListElement)
        return;
    fetch(absoluteUrl + "item/list")
        .then(
            response => {
                var itemListText = "";
                let data = response.json();
                for (let item of data.items) {
                    itemListText += "<ul>\n";
                    itemListText += `<li>Name: ${item.name}</li>\n`;
                    itemListText += `<li>Quantity: ${item.quantity}</li>\n`;
                    itemListText += `<li>ID: ${item.id}</li>\n`;
                    itemListText += `<li>Approved: ${item.approval}</li>\n`;
                    itemListText += "</ul>\n<br/>\n";
                    itemListText += `<button type="button" id="button1-${item.id}" onclick="approveItem(${item.id})">Approved?</button>\n`;
                    itemListText += `<button type="button" id="button2-${item.id}" onclick="unapproveItem(${item.id})>Unapproved?</button>\n`;
                    itemListText += "<br/>\n";
                }
                itemListElement.innerHTML = itemListText;
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
    const authMsgElement = document.getElementById("auth-message");
    if (authMsgElement)
        authMsgElement.style.display = "none";
}

GenerateItemList();