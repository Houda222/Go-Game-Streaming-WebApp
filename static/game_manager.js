"use strict";

const controls = document.getElementById("camera-feed");

document.addEventListener("DOMContentLoaded", function () {
    var buttons = document.querySelectorAll('.btn-petit');

    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            var form = document.getElementById('move');
            var formData = new FormData(form);

            formData.append('psw2', button.value);

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/game', true);

            xhr.onload = function () {
                // Handle the response if needed
                console.log(xhr.responseText);
            };

            xhr.send(formData);
        });
    });
});