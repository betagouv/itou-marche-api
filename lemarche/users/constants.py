KIND_SIAE = "SIAE"  # Structure inclusive qui souhaite proposer ses offres
KIND_SIAE_DISPLAY = "Structure"
KIND_BUYER = "BUYER"  # Un acheteur qui souhaite réaliser un achat inclusif
KIND_BUYER_DISPLAY = "Acheteur"
KIND_PARTNER = "PARTNER"
KIND_PARTNER_DISPLAY = "Partenaire"
KIND_INDIVIDUAL = "INDIVIDUAL"
KIND_INDIVIDUAL_DISPLAY = "Particulier"
KIND_ADMIN = "ADMIN"
KIND_ADMIN_DISPLAY = "Administrateur"  # Administrateur.trice

KIND_CHOICES = (
    (KIND_SIAE, KIND_SIAE_DISPLAY),
    (KIND_BUYER, KIND_BUYER_DISPLAY),
    (KIND_PARTNER, KIND_PARTNER_DISPLAY),
    (KIND_INDIVIDUAL, KIND_INDIVIDUAL_DISPLAY),
)
KIND_CHOICES_WITH_ADMIN = KIND_CHOICES + ((KIND_ADMIN, KIND_ADMIN_DISPLAY),)


BUYER_KIND_PUBLIC = "PUBLIC"
BUYER_KIND_PRIVATE = "PRIVE"
BUYER_KIND_CHOICES = (
    (BUYER_KIND_PUBLIC, "Public"),
    (BUYER_KIND_PRIVATE, "Privé"),
)
BUYER_KIND_DETAIL_PRIVATE_BIG_CORP = "PRIVATE_BIG_CORP"
BUYER_KIND_DETAIL_PRIVATE_ETI = "PRIVATE_ETI"
BUYER_KIND_DETAIL_PRIVATE_PME = "PRIVATE_PME"
BUYER_KIND_DETAIL_PRIVATE_TPE = "PRIVATE_TPE"
BUYER_KIND_DETAIL_PUBLIC_ASSOCIATION = "PUBLIC_ASSOCIATION"
BUYER_KIND_DETAIL_PUBLIC_COLLECTIVITY = "PUBLIC_COLLECTIVITY"
BUYER_KIND_DETAIL_PUBLIC_ESTABLISHMENT = "PUBLIC_ESTABLISHMENT"
BUYER_KIND_DETAIL_PUBLIC_MINISTRY = "PUBLIC_MINISTRY"
BUYER_KIND_DETAIL_CHOICES = (
    (BUYER_KIND_DETAIL_PRIVATE_BIG_CORP, "Grand groupe (+5000 salariés)"),
    (BUYER_KIND_DETAIL_PRIVATE_ETI, "ETI (+250 salariés)"),
    (BUYER_KIND_DETAIL_PRIVATE_PME, "PME (+10 salariés)"),
    (BUYER_KIND_DETAIL_PRIVATE_TPE, "TPE"),
    (BUYER_KIND_DETAIL_PUBLIC_ASSOCIATION, "Association"),
    (BUYER_KIND_DETAIL_PUBLIC_COLLECTIVITY, "Collectivité"),
    (BUYER_KIND_DETAIL_PUBLIC_ESTABLISHMENT, "Établissement public"),
    (BUYER_KIND_DETAIL_PUBLIC_MINISTRY, "Ministère"),
)

PARTNER_KIND_FACILITATOR = "FACILITATEUR"
PARTNER_KIND_NETWORD_IAE = "RESEAU_IAE"
PARTNER_KIND_NETWORK_HANDICAP = "RESEAU_HANDICAP"
PARTNER_KIND_DREETS = "DREETS"
PARTNER_KIND_PRESCRIBER = "PRESCRIPTEUR"
PARTNER_KIND_PUBLIC = "PUBLIC"
PARTNER_KIND_PRIVATE = "PRIVE"
PARTNER_KIND_OTHER = "AUTRE"
PARTNER_KIND_CHOICES = (
    (PARTNER_KIND_FACILITATOR, "Facilitateur des clauses sociales"),
    (PARTNER_KIND_NETWORD_IAE, "Réseaux IAE"),
    (PARTNER_KIND_NETWORK_HANDICAP, "Réseau secteur Handicap"),
    (PARTNER_KIND_DREETS, "DREETS / DDETS"),
    (PARTNER_KIND_PRESCRIBER, "Prescripteur"),
    (PARTNER_KIND_PUBLIC, "Organisme public"),
    (PARTNER_KIND_PRIVATE, "Organisme privé"),
    (PARTNER_KIND_OTHER, "Autre"),
)

SOURCE_SIGNUP_FORM = "SIGNUP_FORM"
SOURCE_TALLY_FORM = "TALLY_FORM"
SOURCE_TENDER_FORM = "TENDER_FORM"
SOURCE_DJANGO_ADMIN = "DJANGO_ADMIN"

SOURCE_CHOICES = (
    (SOURCE_SIGNUP_FORM, "Formulaire d'inscription"),
    (SOURCE_TALLY_FORM, "Formulaire verticale"),
    (SOURCE_TENDER_FORM, "Formulaire de dépôt de besoin"),
    (SOURCE_DJANGO_ADMIN, "Admin Django"),
)
