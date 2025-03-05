from django import forms

from lemarche.siaes.models import Siae
from lemarche.tenders.models import QuestionAnswer, Tender


class TenderAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact_email_list"].delimiter = ";"  # Or whichever other character you want.

    class Meta:
        model = Tender
        fields = "__all__"


class QuestionAnswerForm(forms.ModelForm):
    class Meta:
        model = QuestionAnswer
        fields = ["answer"]
        widgets = {
            # client side validation
            "answer": forms.Textarea(attrs={"required": "required"}),
        }


class SiaeSelectionForm(forms.Form):
    siae = forms.ModelMultipleChoiceField(
        queryset=Siae.objects.none(),
    )

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["siae"].queryset = queryset
