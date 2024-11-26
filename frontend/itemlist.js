import("https://code.jquery.com/jquery-3.7.1.min.js");
import("autologin.js");
var orderId = -1;
var orderStatus = -1;

$(document).ready(function () {
    if (localStorage.apikey) {
        autoLogin();
    }
    $.ajax({
        type: "GET",
        url: "http://dankpadserver.jordynsblog.org:5000/item/list",
        headers: {
            Authorization: "Bearer " + localStorage.getItem("apikey")
        },
        success: onGetItemList()
    });
    $("#delete-order-button").click(deleteOrder());
});

function deleteOrder() {
    $.ajax({
        type: "DELETE",
        url: `http://dankpadserver.jordynsblog.org:5000/order/${orderId}/delete`,
        headers: {
            Authorization: "Bearer " + localStorage.getItem("apikey")
        },
        success: onGetItemList()
    });
}

function addItem(itemId) {
    $.ajax({
        type: "POST",
        url: `http://dankpadserver.jordynsblog.org:5000/order/${orderId}/add/${itemId}/1`,
        headers: {
            Authorization: "Bearer " + localStorage.getItem("apikey")
        },
    });
}

function deleteItem(itemId) {
    $.ajax({
        type: "DELETE",
        url: `http://dankpadserver.jordynsblog.org:5000/order/${orderId}/delete/${itemId}/1`,
        headers: {
            Authorization: "Bearer " + localStorage.getItem("apikey")
        },
    });
}

function onGetItemList() {
    $.ajax({
        type: "POST",
        url: "http://dankpadserver.jordynsblog.org:5000/order/create",
        headers: {
            Authorization: "Bearer " + localStorage.getItem("apikey")
        },
        success: function (response) {
            orderId = response.id;
            orderStatus = response.orderstatus;
            $("#order-messsage").innerText = `Order ${orderId} created with status ${orderStatus}.`;
        }
    });
    $.ajax({
        type: "GET",
        url: "http://dankpadserver.jordynsblog.org:5000/item/list",
        headers: {
            Authorization: "Bearer " + localStorage.getItem("apikey")
        },
        success: function (response) {
            var itemListText = "";
            for (let item of response.items) {
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