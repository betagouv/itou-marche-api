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

AMOUNT_RANGE_LIST = [amount[0] for amount in AMOUNT_RANGE_CHOICES]


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
    (SURVEY_NOT_ENCOURAGED_ONLY_BY_US, "Un outil parmi d’autres"),
    (SURVEY_YES, "Oui"),
)

STATUS_DRAFT = "DRAFT"
STATUS_PUBLISHED = "PUBLISHED"
STATUS_VALIDATED = "VALIDATED"

STATUS_CHOICES = (
    (STATUS_DRAFT, "Brouillon"),
    (STATUS_PUBLISHED, "Publié"),
    (STATUS_VALIDATED, "Validé"),
)
