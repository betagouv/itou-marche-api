from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserCreationForm

from lemarche.users.models import User
from lemarche.utils.password_validation import CnilCompositionPasswordValidator


class SignupForm(UserCreationForm):
    KIND_CHOICES_FORM = (
        (User.KIND_SIAE, "Une entreprise sociale inclusive (SIAE ou structure du handicap, GEIQ)"),
        (User.KIND_BUYER, "Un acheteur"),
        (User.KIND_PARTNER, "Un partenaire (réseaux, facilitateurs)"),
    )

    kind = forms.ChoiceField(label="", widget=forms.RadioSelect, choices=KIND_CHOICES_FORM, required=True)
    first_name = forms.CharField(
        label="Votre prénom", widget=forms.TextInput(attrs={"autofocus": "autofocus"}), required=True
    )
    last_name = forms.CharField(label="Votre nom", required=True)
    phone = forms.CharField(
        label="Votre numéro de téléphone",
        max_length=35,
        required=False,
    )
    # company_name is hidden by default in the frontend. Shown if the user choses kind BUYER or PARTNER
    company_name = forms.CharField(
        label="Le nom de votre structure",
        required=False,
    )
    # position is hidden by default in the frontend. Shown if the user choses kind BUYER
    position = forms.CharField(
        label="Votre poste",
        required=False,
    )
    email = forms.EmailField(
        label="Votre adresse e-mail",
        widget=forms.TextInput(attrs={"placeholder": "Merci de bien vérifier l'adresse saisie."}),
        required=True,
    )
    # help_text="Nous enverrons un e-mail de confirmation à cette adresse avant de valider le compte.")

    accept_rgpd = forms.BooleanField(label=User._meta.get_field("accept_rgpd").help_text, help_text="", required=True)
    # accept_survey is hidden by default in the frontend. Shown if the user choses kind BUYER or PARTNER
    accept_survey = forms.BooleanField(
        label=User._meta.get_field("accept_survey").help_text, help_text="", required=False
    )

    class Meta:
        model = User
        fields = [
            "kind",
            "first_name",
            "last_name",
            "phone",
            "company_name",
            "email",
            "password1",
            "password2",
            "accept_rgpd",
            "accept_survey",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # password validation rules
        self.fields["password1"].help_text = CnilCompositionPasswordValidator().get_help_text()

    def clean_email(self):
        email = self.cleaned_data["email"]
        return email.lower()


class LoginForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data["username"]
        return username.lower()


class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Votre adresse e-mail", required=True)
