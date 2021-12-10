document.addEventListener("DOMContentLoaded", function() {
    $('#favorite_item_remove_modal').on('show.bs.modal', function (event) {
        // Button that triggered the modal
        var button = $(event.relatedTarget);

        // Extract info from data-* attributes
        var siaeId = button.data('siae-id');
        var siaeSlug = button.data('siae-slug');
        var siaeNameDisplay = button.data('siae-name-display');

        // Update the modal's content
        // - siae name display
        // - check favorite lists that already contain the siae
        // - edit the form action url
        var modal = document.querySelector('#favorite_item_remove_modal');
        var modalForm = modal.querySelector('form');
        modal.querySelector('#siae-name-display').textContent = siaeNameDisplay;
        var formActionUrl = modalForm.getAttribute('action');
        modalForm.setAttribute('action', formActionUrl.replace('siae-slug-to-replace', siaeSlug));
    });
});
