document.addEventListener('alpine:init', function () {
    Alpine.data('activityItem', () => ({
        siaeSlug: null,
        siaeActivityId: null,
        siaeActivityNameDisplay: null,

        initOptions(siaeSlug, siaeActivityId, siaeActivityNameDisplay) {
            this.siaeSlug = siaeSlug;
            this.siaeActivityId = siaeActivityId;
            this.siaeActivityNameDisplay = siaeActivityNameDisplay;
        },
        remove() {
            // Update the modal's content
            // - siae activity name display
            // - edit the form action url
            // - open the modal
            let modalID = 'siae_activity_delete_modal';
            let modal = document.querySelector(`#${modalID}`);
            let modalForm = modal.querySelector('form');
            if (modal.querySelector('#siae-activity-name-display')) {
                modal.querySelector('#siae-activity-name-display').textContent = this.siaeActivityNameDisplay;
            }
            let formActionUrl = escapeHtml(modalForm.getAttribute('data-action'));
            modalForm.setAttribute('action', formActionUrl.replace('siae-slug-to-replace', this.siaeSlug).replace('siae-activity-id-to-replace', this.siaeActivityId));

            const modalDialog = document.getElementById(modalID);
            dsfr(modalDialog).modal.disclose();
        }
    }));
});
