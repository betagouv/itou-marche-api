document.addEventListener('DOMContentLoaded', function() {
    /**
     * Multiselect dropdown for the kind search form field
     */

    const kindFormElement = document.querySelector('#search-form #id_kind');
    const kindFormPlaceholder = '';

    const buttonTextAndTitle = function(options, select) {
        if (options.length === 0) {
            return kindFormPlaceholder;
        }
        else if (options.length > 2) {
            return `${options.length} types sélectionnés`;
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

    // only on pages with id_kind
    if (document.body.contains(kindFormElement)) {
        $('#id_kind').multiselect({
            // height & width
            maxHeight: 400,
            buttonWidth: '100%',
            widthSynchronizationMode: 'always',
            // button
            buttonTextAlignment: 'left',
            buttonText: buttonTextAndTitle,
            buttonTitle: buttonTextAndTitle,
            // other
            widthSynchronizationMode: 'ifPopupIsSmaller',
            // enableHTML: true,
            // nonSelectedText: `<span class="text-muted">${kindFormPlaceholder}</span>`,
        });

        // hack to set the placeholder color to grey when there is no kind selected
        const multiselectSelectedText = document.querySelector('.multiselect-selected-text');
        if (multiselectSelectedText.innerText === kindFormPlaceholder) {
            multiselectSelectedText.classList.add('text-muted');
        }
        multiselectSelectedText.addEventListener('DOMSubtreeModified', function () {
            if (this.innerText === kindFormPlaceholder) {
                this.classList.add('text-muted');
            } else {
                this.classList.remove('text-muted');
            }
        })
    }

});
