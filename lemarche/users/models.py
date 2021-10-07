from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class UserQueryset(models.QuerySet):
    """
    Custom queryset with additional filtering methods for users.
    """

    def siae_admins(self):
        """Only return users who are linked to a SIAE."""
        return self.filter(siaes__isnull=False)

    def with_api_key(self):
        """Only return users with an API Key."""
        return self.filter(api_key__isnull=False)


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def get_queryset(self):
        return UserQueryset(self.model, using=self._db)

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("Il manque le champ E-mail")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superuser doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def siae_admins(self):
        """Only return users who are linked to a SIAE."""
        return self.get_queryset().siae_admins()

    def with_api_key(self):
        """Only return users with an API Key."""
        return self.get_queryset().with_api_key()


class User(AbstractUser):
    """
    C4 Custom User Model
    """

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    ACCOUNT_USER_MODEL_USERNAME_FIELD = None
    ACCOUNT_USERNAME_REQUIRED = False
    ACCOUNT_EMAIL_REQUIRED = True

    # KIND_PERSO = "PERSO"  # PERSON_TYPE_NATURAL / 1
    # KIND_COMPANY = "COMPANY"  # PERSON_TYPE_LEGAL / 2 (not used)
    KIND_SIAE = "SIAE"  # PERSON_TYPE_INCLUSIVE / 4
    KIND_BUYER = "BUYER"  # PERSON_TYPE_CLASSIC / 3
    KIND_PARTNER = "PARTNER"  # PERSON_TYPE_PARTNER / 6
    KIND_ADMIN = "ADMIN"  # PERSON_TYPE_ADMIN/ 5

    KIND_CHOICES = (
        # (KIND_PERSO, "Utilisateur"),  # Une personne
        # (KIND_COMPANY, "Entreprise"),  # Une entreprise
        (KIND_SIAE, "Structure"),  # Structure inclusive qui souhaite proposer ses offres
        (KIND_BUYER, "Acheteur"),  # Un acheteur qui souhaite réaliser un achat inclusif
        (KIND_PARTNER, "Partenaire"),  # Partenaire
    )

    KIND_CHOICES_WITH_ADMIN = KIND_CHOICES + ((KIND_ADMIN, "Administrateur"),)  # Administrateur.trice

    username = None
    email = models.EmailField(verbose_name="Adresse e-mail", unique=True)
    first_name = models.CharField("Prénom", max_length=150)
    last_name = models.CharField("Nom", max_length=150)
    kind = models.CharField(verbose_name="Type", max_length=20, choices=KIND_CHOICES_WITH_ADMIN, blank=True, null=True)
    phone = models.CharField(verbose_name="Téléphone", max_length=20, blank=True, null=True)
    api_key = models.CharField(verbose_name="Clé API", max_length=128, unique=True, blank=True, null=True)

    c4_id = models.IntegerField(blank=True, null=True)
    c4_phone_prefix = models.CharField(verbose_name="Indicatif international", max_length=20, blank=True, null=True)
    c4_time_zone = models.CharField(verbose_name="Fuseau", max_length=150, blank=True, null=True)
    c4_website = models.URLField(verbose_name="Site web", blank=True, null=True)
    c4_company_name = models.CharField(verbose_name="Nom de l'entreprise", max_length=255, blank=True, null=True)
    c4_siret = models.CharField(verbose_name="Siret ou Siren", max_length=14, blank=True, null=True)
    c4_naf = models.CharField(verbose_name="Naf", max_length=5, blank=True, null=True)
    c4_phone_verified = models.BooleanField(default=False)
    c4_email_verified = models.BooleanField(default=False)
    c4_id_card_verified = models.BooleanField(default=False)
    c4_accept_survey = models.BooleanField(
        help_text="J'accepte de répondre à une enquête deux fois par an afin de permettre de mesurer la progression des achats inclusifs en France",  # noqa
        default=False,
    )
    c4_accept_rgpd = models.BooleanField(help_text="J'accepte les conditions d'utilisation du service", default=False)
    c4_offers_for_pro_sector = models.BooleanField(
        help_text="Je m'engage à ce que les offres déposées sur la Place de marché soient destinées à des structures professionnelles (association, secteur privé ou public)",  # noqa
        default=False,
    )
    c4_quote_promise = models.BooleanField(
        help_text="Je m'engage à traiter les demandes de devis qui me seront adressées (soumettre un devis, solliciter des informations complémentaires ou  refuser une demande constituent des réponses)",  # noqa
        default=False,
    )

    # is_active, is_staff, is_superuser

    # date_joined, last_login
    created_at = models.DateTimeField(verbose_name="Date de création", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="Date de mise à jour", auto_now=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def short_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name.upper()[:1]}. {self.last_name.upper()}"
        return ""
