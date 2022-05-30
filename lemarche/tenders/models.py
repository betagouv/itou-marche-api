from datetime import datetime
from functools import reduce
from uuid import uuid4

import _operator
from django.conf import settings
from django.db import IntegrityError, models, transaction
from django.db.models import Case, Count, F, IntegerField, Q, Sum, When
from django.db.models.functions import Greatest
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify

from lemarche.utils.fields import ChoiceArrayField


class TenderQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(author=user)

    def validated(self):
        return self.filter(validated_at__isnull=False)

    def is_live(self):
        return self.validated().filter(deadline_date__gte=datetime.today())

    def in_perimeters(self, post_code, department, region):
        filters = (
            Q(perimeters__post_codes__contains=[post_code])
            | Q(perimeters__insee_code=department)
            | Q(perimeters__name=region)
        )
        # add distance?
        return self.filter(filters).distinct()

    def in_sectors(self, sectors):
        if sectors:
            query = reduce(_operator.or_, (Q(sectors__id__contains=item.id) for item in sectors))
            return self.filter(query).distinct()
        else:
            return self

    def filter_with_siae(self, siae):
        """
        Return the list of tenders corresponding to the Siae
        Filters on its sectors & perimeter
        """
        sectors = siae.sectors.all()
        qs = self.prefetch_related("sectors", "perimeters").in_sectors(sectors)
        if siae.geo_range != siae.GEO_RANGE_COUNTRY:
            qs.in_perimeters(post_code=siae.post_code, department=siae.department, region=siae.region)
        return qs.distinct()

    def with_siae_stats(self):
        """
        Enrich each Tender with stats on their linked Siae
        """
        return self.annotate(
            siae_count=Count("siaes", distinct=True),
            siae_email_send_count=Sum(
                Case(When(tendersiae__email_send_date__isnull=False, then=1), default=0, output_field=IntegerField())
            ),
            siae_detail_display_count=Sum(
                Case(
                    When(tendersiae__detail_display_date__isnull=False, then=1), default=0, output_field=IntegerField()
                )
            ),
            siae_contact_click_count=Sum(
                Case(
                    When(tendersiae__contact_click_date__isnull=False, then=1), default=0, output_field=IntegerField()
                )
            ),
            siae_contact_click_since_last_seen_date_count=Sum(
                Case(
                    When(
                        tendersiae__contact_click_date__gte=Greatest(
                            F("siae_interested_list_last_seen_date"), F("created_at")
                        ),
                        then=1,
                    ),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )


class Tender(models.Model):
    """Appel d'offres et devis"""

    AMOUNT_RANGE_0 = "<25K"
    AMOUNT_RANGE_1 = "<100K"
    AMOUNT_RANGE_2 = "<1M"
    AMOUNT_RANGE_3 = "<5M"
    AMOUNT_RANGE_4 = ">5M"

    AMOUNT_RANGE_CHOICES = (
        (AMOUNT_RANGE_0, "0-25K €"),
        (AMOUNT_RANGE_1, "25K-100K €"),
        (AMOUNT_RANGE_2, "100K-1M €"),
        (AMOUNT_RANGE_3, "1M-5M €"),
        (AMOUNT_RANGE_4, "> 5M €"),
    )

    TENDER_KIND_TENDER = "TENDER"
    TENDER_KIND_QUOTE = "QUOTE"
    TENDER_KIND_BOAMP = "BOAMP"
    TENDER_KIND_PROJECT = "PROJ"

    TENDER_KIND_CHOICES = (
        (TENDER_KIND_TENDER, "Appel d'offres"),
        (TENDER_KIND_QUOTE, "Devis"),
        (TENDER_KIND_PROJECT, "Sourcing"),
    )

    RESPONSE_KIND_EMAIL = "EMAIL"
    RESPONSE_KIND_TEL = "TEL"
    RESPONSE_KIND_EXTERNAL = "EXTERN"

    RESPONSE_KIND_CHOICES = (
        (RESPONSE_KIND_EMAIL, "E-mail"),
        (RESPONSE_KIND_TEL, "Téléphone"),
        (RESPONSE_KIND_EXTERNAL, "Lien externe"),
    )

    title = models.CharField(verbose_name="Titre du besoin", max_length=255)
    slug = models.SlugField(verbose_name="Slug", max_length=255, unique=True)
    kind = models.CharField(
        verbose_name="Type de besoin", max_length=6, choices=TENDER_KIND_CHOICES, default=TENDER_KIND_TENDER
    )
    description = models.TextField(verbose_name="Description du besoin", blank=True)
    constraints = models.TextField(verbose_name="Contraintes techniques spécifiques", blank=True)
    external_link = models.URLField(verbose_name="Lien vers l'appel d'offres", blank=True)
    deadline_date = models.DateField(verbose_name="Date de clôture des réponses")
    start_working_date = models.DateField(verbose_name="Date idéale de début des prestations", blank=True, null=True)
    amount = models.CharField(
        verbose_name="Montant du marché", max_length=9, choices=AMOUNT_RANGE_CHOICES, blank=True, null=True
    )
    response_kind = ChoiceArrayField(
        models.CharField(max_length=6, choices=RESPONSE_KIND_CHOICES),
        verbose_name="Comment souhaitez-vous être contacté ?",
    )

    contact_first_name = models.CharField(verbose_name="Prénom du contact", max_length=255, blank=True)
    contact_last_name = models.CharField(verbose_name="Nom de famille du contact", max_length=255, blank=True)
    contact_email = models.EmailField(verbose_name="E-mail du contact", blank=True)
    contact_phone = models.CharField(verbose_name="Téléphone du contact", max_length=20, blank=True)

    is_country_area = models.BooleanField(verbose_name="France entière", default=False)

    perimeters = models.ManyToManyField(
        "perimeters.Perimeter", verbose_name="Lieux d'exécution", related_name="tenders", blank=True
    )

    sectors = models.ManyToManyField(
        "sectors.Sector", verbose_name="Secteurs d'activité", related_name="tenders", blank=False
    )

    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name="Auteur",
        related_name="tenders",
        on_delete=models.CASCADE,
        blank=True,
    )

    siaes = models.ManyToManyField(
        "siaes.Siae",
        through="tenders.TenderSiae",
        verbose_name="Structures correspondantes au besoin",
        related_name="tenders",
        blank=True,
    )

    # stats
    siae_interested_list_last_seen_date = models.DateTimeField(
        "Date de dernière visite de l'auteur sur la page 'structures intéressées'", blank=True, null=True
    )

    created_at = models.DateTimeField(verbose_name="Date de création", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="Date de modification", auto_now=True)
    validated_at = models.DateTimeField("Date de validation", blank=True, null=True)

    objects = models.Manager.from_queryset(TenderQuerySet)()

    class Meta:
        verbose_name = "Besoin d'acheteur"
        verbose_name_plural = "Besoins des acheteurs"
        ordering = ["-updated_at", "deadline_date"]

    def __str__(self):
        return self.title

    def set_slug(self, with_uuid=False):
        """
        The slug field should be unique.
        """
        if not self.slug:
            self.slug = f"{slugify(self.title)[:40]}-{str(self.author.company_name or '')}"
        if with_uuid:
            self.slug += f"-{str(uuid4())[:4]}"

    def save(self, *args, **kwargs):
        """
        - update the object stats
        - update the object content_fill_dates
        - generate the slug field
        """
        try:
            self.set_slug()
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError as e:
            # check that it's a slug conflict
            # Full message expected: duplicate key value violates unique constraint "tenders_tender_slug_0f0b821f_uniq" DETAIL:  Key (slug)=(...) already exists.  # noqa
            if "tenders_tender_slug" in str(e):
                self.set_slug(with_uuid=True)
                super().save(*args, **kwargs)
            else:
                raise e

    @cached_property
    def get_contact_full_name(self):
        return f"{self.contact_first_name} {self.contact_last_name}"

    @cached_property
    def get_sectors_names(self):
        return ", ".join(self.sectors.values_list("name", flat=True))

    @cached_property
    def get_perimeters_names(self):
        return ", ".join(self.perimeters.values_list("name", flat=True))

    @cached_property
    def can_display_contact_email(self):
        return self.RESPONSE_KIND_EMAIL in self.response_kind and self.contact_email

    @cached_property
    def can_display_contact_phone(self):
        return self.RESPONSE_KIND_TEL in self.response_kind and self.contact_phone

    @cached_property
    def can_display_contact_external_link(self):
        return self.RESPONSE_KIND_EXTERNAL in self.response_kind and self.external_link

    def get_absolute_url(self):
        return reverse("tenders:detail", kwargs={"slug": self.slug})


class TenderSiae(models.Model):
    TENDER_SIAE_SOURCE_EMAIL = "EMAIL"
    TENDER_SIAE_SOURCE_DASHBOARD = "DASHBOARD"
    TENDER_SIAE_SOURCE_CHOICES = (
        (TENDER_SIAE_SOURCE_EMAIL, "E-mail"),
        (TENDER_SIAE_SOURCE_DASHBOARD, "Dashboard"),
    )

    tender = models.ForeignKey("tenders.Tender", verbose_name="Besoin d'acheteur", on_delete=models.CASCADE)
    siae = models.ForeignKey("siaes.Siae", verbose_name="Structure", on_delete=models.CASCADE)

    source = models.CharField(max_length=20, choices=TENDER_SIAE_SOURCE_CHOICES, default=TENDER_SIAE_SOURCE_EMAIL)

    # stats
    email_send_date = models.DateTimeField("Date d'envoi de l'e-mail", blank=True, null=True)
    detail_display_date = models.DateTimeField("Date de visualisation du besoin", blank=True, null=True)
    contact_click_date = models.DateTimeField("Date de clic sur les coordonnées du besoin", blank=True, null=True)

    created_at = models.DateTimeField(verbose_name="Date de création", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="Date de modification", auto_now=True)

    class Meta:
        verbose_name = "Structure correspondant au besoin"
        verbose_name_plural = "Structures correspondantes au besoin"
        ordering = ["-created_at"]
