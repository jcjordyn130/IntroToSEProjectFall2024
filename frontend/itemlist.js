var orderId = -1;
var orderStatus = -1;

$(document).ready(function () {
    $.ajax({
        type: "GET",
        url: "http://dankpadserver.jordynsblog.org:5000/item/list",
        success: onGetItemList()
    });
    $("#delete-order-button").click(deleteOrder());
});

function deleteOrder() {
    $.ajax({
        type: "DELETE",
        url: `http://dankpadserver.jordynsblog.org:5000/order/${orderId}/delete`,
        success: onGetItemList()
    });
}

function addItem(itemId) {
    $.ajax({
        type: "POST",
        url: `http://dankpadserver.jordynsblog.org:5000/order/${orderId}/add/${itemId}/1`
    });
}

function deleteItem(itemId) {
    $.ajax({
        type: "DELETE",
        url: `http://dankpadserver.jordynsblog.org:5000/order/${orderId}/delete/${itemId}/1`
    });
}

function onGetItemList() {
    $.ajax({
        type: "POST",
        url: "http://dankpadserver.jordynsblog.org:5000/order/create",
        success: function (response) {
            let data = response.json();
            orderId = data.id;
            orderStatus = data.orderstatus; // Is this correct?
            $("#order-messsage").innerText = `Order ${orderId} created with status ${orderStatus}.`;
        }
    });
    $.ajax({
        type: "GET",
        url: "http://dankpadserver.jordynsblog.org:5000/item/list",
        success: function (response) {
            let data = response.json();
            var itemListText = "";
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
            $("#item-list").html(itemListText);
        }
    });
}