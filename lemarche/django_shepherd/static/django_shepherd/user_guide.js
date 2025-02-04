class UserGuide {
    constructor() {
        this.tour = new Shepherd.Tour({
            useModalOverlay: true,
            confirmCancel: true,
            confirmCancelMessage: "Ëtes-vous sûr d'annuler ce guide des foncctionnalités ? Il ne vous sera plus proposé",
            defaultStepOptions: {
                classes: 'shepherd-theme-arrows',
                scrollTo: {
                    behavior: 'smooth',
                    block: 'center'
                },
            }
        });

        // Once cancelled or completed
        this.tour.on("cancel", this.onTourEnd);
        this.tour.on("complete", this.onTourEnd);
    }

    init() {
        document.addEventListener('startUserGuide', (event) => {
            const guideName = event.detail.guideName;
            this.startGuide(guideName);
        });

        // Listen to htmx events
        document.body.addEventListener('htmx:afterSwap', (event) => {
            if (event.detail.target.id === 'guideContainer') {
                const guideName = event.detail.target.getAttribute('data-guide-name');
                this.startGuide(guideName);
            }
        });
    }
    /*Called on ending tour events. Call an url to add the user to already viewed guides*/
    onTourEnd() {
        // Here "this" represents "Tour" instance
        fetch(`/django_shepherd/viewed_guide/${this.guideName}/`)
    }

    startGuide(guideName) {
        this.tour.guideName = guideName
        fetch(`/django_shepherd/get_guide/${guideName}/`)
            .then(response => response.json())
            .then(data => {
                this.tour.steps = []; // Clear previous steps
                data.steps.forEach((step, index) => {
                    const isFirstStep = index === 0;
                    const isLastStep = index === data.steps.length - 1;
                    this.tour.addStep({
                        title: step.title,
                        text: step.text,
                        attachTo: {
                            element: step.element,
                            on: step.position
                        },
                        buttons: [
                            !isLastStep && {
                                text: 'Ignorer',
                                action: this.tour.cancel,
                                classes: 'btn btn-secondary'
                            },
                            !isFirstStep && {
                                text: 'Précédent',
                                action: this.tour.back,
                                classes: 'btn btn-primary'
                            },
                            {
                                text: isLastStep ? 'Finir' : 'Suivant',
                                action: this.tour.next,
                                classes: 'btn ' + (isLastStep ? 'btn-success' : 'btn-primary')
                            }
                        ].filter(Boolean)
                    });
                });
                this.tour.start();
            });
    }
}
