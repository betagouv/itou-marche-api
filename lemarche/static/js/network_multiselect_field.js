document.addEventListener('DOMContentLoaded', function() {
    /**
     * Multiselect dropdown for the network search form field
     */

    const FORM_INPUT_ID = "id_networks";
    const FORM_MULTISELECT_ID = `${FORM_INPUT_ID}_multiselect`;
    const FORM_ELEMENT = document.querySelector(`.use-multiselect #${FORM_INPUT_ID}`);
    const FORM_PLACEHOLDER = 'Choisir…';

    const buttonTextAndTitle = function(options, select) {
        if (options.length === 0) {
            return FORM_PLACEHOLDER;
        }
        else if (options.length > 2) {
            return `${options.length} réseaux sélectionnés`;
        }
        else {
            var labels = [];
            options.each(function() {
                if ($(this).attr('label') !== undefined) {
                    labels.push($(this).attr('label'));
                }
                else {
                    labels.push($(this).html());
                }
            });
            return labels.join(', ') + '';
        }
    }

    if (document.body.contains(FORM_ELEMENT)) {
        $(`#${FORM_INPUT_ID}`).multiselect({
            // height & width
            maxHeight: 400,
            buttonWidth: '100%',
            widthSynchronizationMode: 'always',
            // button
            buttonTextAlignment: 'left',
            buttonText: buttonTextAndTitle,
            buttonTitle: buttonTextAndTitle,
            // filter options
            enableFiltering: true,
            enableCaseInsensitiveFiltering: true,
            filterPlaceholder: FORM_PLACEHOLDER,
            // reset button
            includeResetOption: true,
            includeResetDivider: true,
            resetText: 'Réinitialiser la sélection',
            // enableResetButton: true,
            // resetButtonText: 'Réinitialiser',
            // ability to select all group's child options in 1 click
            enableClickableOptGroups: true,
            // other
            buttonContainer: `<div id="${FORM_MULTISELECT_ID}" class="btn-group" />`,
            widthSynchronizationMode: 'ifPopupIsSmaller',
            // enableHTML: true,
            // nonSelectedText: `<span class="text-muted">${FORM_PLACEHOLDER}</span>`,
            templates: {
                resetButton: '<div class="multiselect-reset p-2"><button type="button" class="btn btn-sm btn-block btn-outline-primary"></button></div>',
                // buttonGroupReset: '<button type="button" class="multiselect-reset btn btn-outline-primary btn-block"></button>'
            }
        });

        // hack to set the placeholder color to grey when there is no sector selected
        const multiselectSelectedText = document.querySelector(`#${FORM_MULTISELECT_ID} .multiselect-selected-text`);
        if (multiselectSelectedText.innerText === FORM_PLACEHOLDER) {
            multiselectSelectedText.classList.add('text-muted');
        }
        multiselectSelectedText.addEventListener('DOMSubtreeModified', function () {
            if (this.innerText === FORM_PLACEHOLDER) {
                this.classList.add('text-muted');
            } else {
                this.classList.remove('text-muted');
            }
        })
    }

});
