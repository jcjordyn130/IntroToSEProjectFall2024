const absoluteUrl = "http://dankpadserver.jordynsblog.org:5000/";
//const absoluteUrl = "./";

var orderId = -1;
var orderStatus = -1;

function CreateOrder() {
    fetch(absoluteUrl + "order/create")
        .then(
            response => {
                orderId = response.id;
                orderStatus = response.orderstatus;
                document.getElementById("order-message").innerText = `Order ${orderId} created with status ${orderStatus}.`;
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

function DeleteOrder() {
    fetch(absoluteUrl + `order/${orderId}/delete`)
        .then(
            response => {
                CreateOrder();
                GenerateItemList();
            }
        )
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

function addItem(itemId) {
    fetch(absoluteUrl + `order/${orderId}/add/${itemId}/1`)
        .catch(
            (e) => {
                console.error(e.message);
            }
        );
}

function deleteItem(itemId) {
    fetch(absoluteUrl + `order/${orderId}/delete/${itemId}/1`)
        .catch(
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
                    itemListText += `<li>Description: ${item.description}</li>\n`;
                    itemListText += `<li>ID: ${item.id}</li>\n`;
                    itemListText += `<li>Approved: ${item.approval}</li>\n`;
                    itemListText += "</ul>\n<br/>\n";
                    itemListText += `<button type="button" id="button1-${item.id}" onclick="addItem(${item.id})">Add?</button>\n`;
                    itemListText += `<button type="button" id="button2-${item.id}" onclick="deleteItem(${item.id})>Delete?</button>\n`;
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
}

CreateOrder();
GenerateItemList();