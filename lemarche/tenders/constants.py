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

# survey choices for yes, no or don't know
SURVEY_NO = "0"
SURVEY_YES = "1"
SURVEY_DONT_KNOW = "?"

SURVEY_YES_NO_DONT_KNOW_CHOICES = (
    (SURVEY_NO, "Non"),
    (SURVEY_YES, "Oui"),
    (SURVEY_DONT_KNOW, "Je ne sais pas"),
)


SURVEY_NOT_ENCOURAGED_ONLY_BY_US = "+"

SURVEY_ENCOURAGED_BY_US_CHOICES = (
    (SURVEY_NO, "Non"),
    (SURVEY_NOT_ENCOURAGED_ONLY_BY_US, "Un outil parmi d'autres"),
    (SURVEY_YES, "Oui"),
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
