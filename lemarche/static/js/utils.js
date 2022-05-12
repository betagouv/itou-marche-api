// https://github.com/betagouv/itou/blob/master/itou/static/js/utils.js

$(document).ready(() => {
    // prevent default on click
    $('.js-prevent-default').on('click', (event) => {
        event.preventDefault();
    });

    // element will be hidden if JS is disabled
    $('.js-display-if-javascript-enabled').css('display', 'block');

    // only way found to select checkbox group titles
    $('#id_sectors').children('.form-check.checkbox-title').contents().filter(function() {
        return this.nodeType == 3;
    }).wrap('<span class="group-title"></span>');
});

let toggleRequiredClasses = (toggle, element) => {
    element.required = required;
    elementToToggle = element.parentNode.classList.contains("form-group") ? element.parentNode : element.parentNode.parentNode;
    if (required) {
        elementToToggle.classList.add('form-group-required');
    } else {
        elementToToggle.classList.remove('form-group-required');
    }
};

let toggleInputElement = (toggle, element, required = undefined) => {
    // function usefull to find element form-group of bootstrap forms
    elementToToggle = element.parentNode.classList.contains("form-group") ? element.parentNode : element.parentNode.parentNode;
    if (toggle) {
        elementToToggle.classList.remove('d-none');
    } else {
        elementToToggle.classList.add('d-none');
    }
    if (required != undefined) {
        toggleRequiredClasses(required, element);
    }
}