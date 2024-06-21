from lemarche.utils import constants


KIND_TENDER = "TENDER"
KIND_TENDER_DISPLAY = "Appel d'offres"
KIND_QUOTE = "QUOTE"
KIND_QUOTE_DISPLAY = "Demande de devis"
KIND_PROJECT = "PROJ"
KIND_PROJECT_DISPLAY = "Sourcing"
KIND_PROJECT_SIAE_DISPLAY = "Projet d'achat"
KIND_BOAMP = "BOAMP"
KIND_CHOICES = (
    (KIND_TENDER, KIND_TENDER_DISPLAY),
    (KIND_QUOTE, KIND_QUOTE_DISPLAY),
    (KIND_PROJECT, KIND_PROJECT_DISPLAY),
)

OLD_AMOUNT_RANGE_0 = "<25K"
OLD_AMOUNT_RANGE_1 = "<100K"
OLD_AMOUNT_RANGE_2 = "<1M"
OLD_AMOUNT_RANGE_3 = "<5M"
OLD_AMOUNT_RANGE_4 = ">5M"

OLD_AMOUNT_RANGE_0_LABEL = "0-25 K€"
OLD_AMOUNT_RANGE_1_LABEL = "25K-100 K€"
OLD_AMOUNT_RANGE_2_LABEL = "100K-1M €"
OLD_AMOUNT_RANGE_3_LABEL = "1M-5M €"
OLD_AMOUNT_RANGE_4_LABEL = "> 5M €"

AMOUNT_RANGE_0_1 = "0-1K"
AMOUNT_RANGE_1_5 = "1-5K"
AMOUNT_RANGE_5_10 = "5-10K"
AMOUNT_RANGE_10_15 = "10-15K"
AMOUNT_RANGE_15_20 = "15-20K"
AMOUNT_RANGE_20_30 = "20-30K"
AMOUNT_RANGE_30_50 = "30-50K"
AMOUNT_RANGE_50_100 = "50-100K"
AMOUNT_RANGE_100_150 = "100-150K"
AMOUNT_RANGE_150_250 = "150-250K"
AMOUNT_RANGE_250_500 = "250-500K"
AMOUNT_RANGE_500_750 = "500-750K"
AMOUNT_RANGE_750_1000 = "750K-1M"
AMOUNT_RANGE_1000_MORE = ">1M"

AMOUNT_RANGE_CHOICES = (
    (AMOUNT_RANGE_0_1, "0-1000 €"),
    (AMOUNT_RANGE_1_5, "1-5 K€"),
    (AMOUNT_RANGE_5_10, "5-10 K€"),
    (AMOUNT_RANGE_10_15, "10-15 K€"),
    (AMOUNT_RANGE_15_20, "15-20 K€"),
    (AMOUNT_RANGE_20_30, "20-30 K€"),
    (AMOUNT_RANGE_30_50, "30-50 K€"),
    (AMOUNT_RANGE_50_100, "50-100 K€"),
    (AMOUNT_RANGE_100_150, "100-150 K€"),
    (AMOUNT_RANGE_150_250, "150-250 K€"),
    (AMOUNT_RANGE_250_500, "250-500 K€"),
    (AMOUNT_RANGE_500_750, "500-750 K€"),
    (AMOUNT_RANGE_750_1000, "750-1000 K€"),
    (AMOUNT_RANGE_1000_MORE, "> 1 M€"),
)

AMOUNT_RANGE_CHOICE_LIST = [amount[0] for amount in AMOUNT_RANGE_CHOICES]

AMOUNT_RANGE_CHOICE_EXACT = {
    AMOUNT_RANGE_0_1: 1000 - 1,  # 1000 €
    AMOUNT_RANGE_1_5: 5 * 10**3 - 1,  # 5000 €
    AMOUNT_RANGE_5_10: 10 * 10**3 - 1,  # 10000 €
    AMOUNT_RANGE_10_15: 15 * 10**3 - 1,  # 15000 €
    AMOUNT_RANGE_15_20: 20 * 10**3 - 1,  # 20000 €
    AMOUNT_RANGE_20_30: 30 * 10**3 - 1,  # 30000 €
    AMOUNT_RANGE_30_50: 50 * 10**3 - 1,  # 50000 €
    AMOUNT_RANGE_50_100: 100 * 10**3 - 1,  # 100000 €
    AMOUNT_RANGE_100_150: 150 * 10**3 - 1,  # 150000 €
    AMOUNT_RANGE_150_250: 250 * 10**3 - 1,  # 250000 €
    AMOUNT_RANGE_250_500: 500 * 10**3 - 1,  # 500000 €
    AMOUNT_RANGE_500_750: 750 * 10**3 - 1,  # 750000 €
    AMOUNT_RANGE_750_1000: 1000 * 10**3 - 1,  # 1000000 €
    AMOUNT_RANGE_1000_MORE: 1000 * 10**3,  # > 1000000 €
}

WHY_AMOUNT_IS_BLANK_DONT_KNOW = "DONT_KNOW"
WHY_AMOUNT_IS_BLANK_DONT_WANT_TO_SHARE = "DONT_WANT_TO_SHARE"
WHY_AMOUNT_IS_BLANK_CHOICES = (
    (WHY_AMOUNT_IS_BLANK_DONT_KNOW, "Je ne connais pas le montant de mon besoin pour le moment"),
    (WHY_AMOUNT_IS_BLANK_DONT_WANT_TO_SHARE, "Je ne souhaite pas communiquer le montant"),
)


STATUS_DRAFT = "DRAFT"
STATUS_PUBLISHED = "PUBLISHED"
STATUS_VALIDATED = "VALIDATED"
STATUS_SENT = "SENT"

STATUS_CHOICES = (
    (STATUS_DRAFT, "Brouillon"),
    (STATUS_PUBLISHED, "Publié"),
    (STATUS_VALIDATED, "Validé"),
    (STATUS_SENT, "Envoyé"),
)


ACCEPT_SHARE_AMOUNT_TRUE = "✅ Montant partagé"
ACCEPT_SHARE_AMOUNT_FALSE = "❌ Montant non partagé"

RESPONSE_KIND_EMAIL = "EMAIL"
RESPONSE_KIND_TEL = "TEL"
RESPONSE_KIND_EXTERNAL = "EXTERN"
RESPONSE_KIND_CHOICES = (
    (RESPONSE_KIND_EMAIL, "E-mail"),
    (RESPONSE_KIND_TEL, "Téléphone"),
    (RESPONSE_KIND_EXTERNAL, "Lien externe"),
)

SOURCE_FORM = "FORM"
SOURCE_FORM_CSRF = "FORM_CSRF"
SOURCE_STAFF_C4_CREATED = "STAFF_C4_CREATED"
SOURCE_API = "API"
SOURCE_TALLY = "TALLY"
SOURCE_CHOICES = (
    (SOURCE_FORM, "Formulaire"),
    (SOURCE_FORM_CSRF, "Formulaire (erreur CSRF)"),
    (SOURCE_STAFF_C4_CREATED, "Staff Marché (via l'Admin)"),
    (SOURCE_API, "API"),
    (SOURCE_TALLY, "TALLY"),
)

TENDER_SIAE_TRANSACTIONED_SOURCE_ADMIN = "ADMIN"
TENDER_SIAE_TRANSACTIONED_SOURCE_AUTHOR = "AUTHOR"
TENDER_SIAE_TRANSACTIONED_SOURCE_SIAE = "SIAE"
TENDER_SIAE_TRANSACTIONED_SOURCE_CHOICES = (
    (TENDER_SIAE_TRANSACTIONED_SOURCE_ADMIN, "Admin"),
    (TENDER_SIAE_TRANSACTIONED_SOURCE_AUTHOR, "Auteur"),
    (TENDER_SIAE_TRANSACTIONED_SOURCE_SIAE, "Structure"),
)

TENDER_SIAE_SOURCE_EMAIL = "EMAIL"
TENDER_SIAE_SOURCE_DASHBOARD = "DASHBOARD"
TENDER_SIAE_SOURCE_LINK = "LINK"
TENDER_SIAE_SOURCE_AI = "AI"

TENDER_SIAE_SOURCE_CHOICES = (
    (TENDER_SIAE_SOURCE_EMAIL, "E-mail"),
    (TENDER_SIAE_SOURCE_DASHBOARD, "Dashboard"),
    (TENDER_SIAE_SOURCE_LINK, "Lien"),
    (TENDER_SIAE_SOURCE_AI, "IA"),
)

TENDER_SIAE_SOURCES_EXCEPT_IA = [
    source[0] for source in TENDER_SIAE_SOURCE_CHOICES if source[0] != TENDER_SIAE_SOURCE_AI
]

TENDER_SIAE_STATUS_EMAIL_SEND_DATE = "EMAIL_SEND_DATE"
TENDER_SIAE_STATUS_EMAIL_SEND_DATE_DISPLAY = "Contactée"
TENDER_SIAE_STATUS_EMAIL_LINK_CLICK_DATE = "EMAIL_LINK_CLICK_DATE"
TENDER_SIAE_STATUS_EMAIL_LINK_CLICK_DATE_DISPLAY = "Cliquée"
TENDER_SIAE_STATUS_DETAIL_DISPLAY_DATE = "DETAIL_DISPLAY_DATE"
TENDER_SIAE_STATUS_DETAIL_DISPLAY_DATE_DISPLAY = "Vue"
TENDER_SIAE_STATUS_DETAIL_CONTACT_CLICK_DATE = "DETAIL_CONTACT_CLICK_DATE"
TENDER_SIAE_STATUS_DETAIL_CONTACT_CLICK_DATE_DISPLAY = "Intéressée"
TENDER_SIAE_STATUS_DETAIL_NOT_INTERESTED_CLICK_DATE = "DETAIL_NOT_INTERESTED_CLICK_DATE"
TENDER_SIAE_STATUS_DETAIL_NOT_INTERESTED_CLICK_DATE_DISPLAY = "Pas intéressée"
TENDER_SIAE_STATUS_CHOICES = (
    (TENDER_SIAE_STATUS_EMAIL_SEND_DATE, TENDER_SIAE_STATUS_EMAIL_SEND_DATE_DISPLAY),
    (TENDER_SIAE_STATUS_EMAIL_LINK_CLICK_DATE, TENDER_SIAE_STATUS_EMAIL_LINK_CLICK_DATE_DISPLAY),
    (TENDER_SIAE_STATUS_DETAIL_DISPLAY_DATE, TENDER_SIAE_STATUS_DETAIL_DISPLAY_DATE_DISPLAY),
    (TENDER_SIAE_STATUS_DETAIL_CONTACT_CLICK_DATE, TENDER_SIAE_STATUS_DETAIL_CONTACT_CLICK_DATE_DISPLAY),
    (TENDER_SIAE_STATUS_DETAIL_NOT_INTERESTED_CLICK_DATE, TENDER_SIAE_STATUS_DETAIL_NOT_INTERESTED_CLICK_DATE_DISPLAY),
)


SURVEY_SCALE_QUESTION_0 = "0"
SURVEY_SCALE_QUESTION_1 = "1"
SURVEY_SCALE_QUESTION_2 = "2"
SURVEY_SCALE_QUESTION_3 = "3"

SURVEY_SCALE_QUESTION_CHOICES = (
    (SURVEY_SCALE_QUESTION_0, "Non"),
    (SURVEY_SCALE_QUESTION_1, "Peu probablement"),
    (SURVEY_SCALE_QUESTION_2, "Très probablement"),
    (SURVEY_SCALE_QUESTION_3, "Oui"),
)

SURVEY_DOESNT_EXIST_QUESTION_DONT_KNOW = "i-dont-know"
SURVEY_DOESNT_EXIST_QUESTION_INTERNET_SEARCH = "internet-search"
SURVEY_DOESNT_EXIST_QUESTION_NETWORKS = "networks"
SURVEY_DOESNT_EXIST_QUESTION_DIRECTORY = "directory"
SURVEY_DOESNT_EXIST_QUESTION_RECOMMENDATIONS = "recommendations"
SURVEY_DOESNT_EXIST_QUESTION_KNOWN_PROVIDERS = "known-providers"
SURVEY_DOESNT_EXIST_QUESTION_PUBLIC_TENDERS = "public-tenders"
SURVEY_DOESNT_EXIST_QUESTION_FACILITATORS = "facilitators"
SURVEY_DOESNT_EXIST_QUESTION_LOCAL_SOURCING = "local-sourcing"

SURVEY_DOESNT_EXIST_QUESTION_CHOICES = (
    (SURVEY_DOESNT_EXIST_QUESTION_DONT_KNOW, "Je ne sais pas"),
    (
        SURVEY_DOESNT_EXIST_QUESTION_INTERNET_SEARCH,
        "Recherche sur Internet (Google, page jaune, recherche sur le web)",
    ),
    (SURVEY_DOESNT_EXIST_QUESTION_NETWORKS, "Réseaux professionnels et partenariats"),
    (SURVEY_DOESNT_EXIST_QUESTION_DIRECTORY, "Annuaire spécialisé (GESAT, UNEA, Handeco)"),
    (
        SURVEY_DOESNT_EXIST_QUESTION_RECOMMENDATIONS,
        "Recommandations et bouche-à-oreille (Réseaux sociaux, recommandations personnelles, collègues)",
    ),
    (SURVEY_DOESNT_EXIST_QUESTION_KNOWN_PROVIDERS, "Prestataires connus et habituels (Fournisseurs actuels)"),
    (
        SURVEY_DOESNT_EXIST_QUESTION_PUBLIC_TENDERS,
        "Appel d'offres et consultations publiques (BOAMP, JOUE, AWS, appels d'offres)",
    ),
    (SURVEY_DOESNT_EXIST_QUESTION_FACILITATORS, "Facilitateurs de clauses sociales"),
    (
        SURVEY_DOESNT_EXIST_QUESTION_LOCAL_SOURCING,
        "Sourcing local et salons professionnels (Recherche locale, salons, événements professionnels)",
    ),
)

# survey choices
SURVEY_YES_NO_DONT_KNOW_CHOICES = (
    (constants.NO, "Non"),
    (constants.YES, "Oui"),
    (constants.DONT_KNOW, "Je ne sais pas"),
)

SURVEY_NOT_ENCOURAGED_ONLY_BY_US = "+"

SURVEY_ENCOURAGED_BY_US_CHOICES = (
    (constants.NO, "Non"),
    (SURVEY_NOT_ENCOURAGED_ONLY_BY_US, "Un outil parmi d'autres"),
    (constants.YES, "Oui"),
)

SURVEY_TRANSACTIONED_ANSWER_CHOICES = (
    (constants.YES, "Oui"),
    (constants.NO, "Non"),
    (constants.DONT_KNOW, "Pas encore"),
)
SURVEY_TRANSACTIONED_ANSWER_CHOICE_LIST = [choice[0] for choice in SURVEY_TRANSACTIONED_ANSWER_CHOICES]
