"use strict";

const controls = document.getElementById("camera-feed");

// for next previous initial final buttons
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


// for undo button
document.addEventListener("DOMContentLoaded", function () {
    var undoButton = document.getElementById('undo-button');

    undoButton.addEventListener('click', function () {
        var undoForm = document.getElementById('undo-form');
        var formData = new FormData(undoForm);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/undo', true);

        xhr.onload = function () {
            // Handle the response if needed
            console.log(xhr.responseText);
        };

        xhr.send(formData);
    });
});

// change position
document.addEventListener("DOMContentLoaded", function () {
    var changePlaceButton = document.getElementById('change-place-button');

    changePlaceButton.addEventListener('click', function () {
        var changePlaceForm = document.getElementById('change');
        var formData = new FormData(changePlaceForm);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/change_place', true);

        xhr.onload = function () {
            // Handle the response if needed
            console.log(xhr.responseText);
        };

        xhr.send(formData);
    });
});
