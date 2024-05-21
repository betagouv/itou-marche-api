import io

import phonenumbers

# from phonenumber_field.phonenumber import PhoneNumber
from django.core.management import call_command
from django.db import connection


def reset_app_sql_sequences(app_name):
    """
    To reset the id indexes of a given app (will impact *all* of the apps' tables)
    https://docs.djangoproject.com/en/3.1/ref/django-admin/#sqlsequencereset
    https://stackoverflow.com/a/44113124
    """
    print(f"Resetting SQL sequences for {app_name}...")
    output = io.StringIO()
    call_command("sqlsequencereset", app_name, stdout=output, no_color=True)
    sql = output.getvalue()
    with connection.cursor() as cursor:
        cursor.execute(sql)
    output.close()
    print("Reset complete!")


def rename_dict_key(dict, key_name_before, key_name_after):
    dict[key_name_after] = dict[key_name_before]
    dict.pop(key_name_before)


def get_choice(choices, key):
    choices = dict(choices)
    if key in choices:
        return choices[key]
    return None


def round_by_base(x, base=5):
    return base * round(x / base)


def date_to_string(date, format="%d/%m/%Y"):
    """
    datetime.date(2022, 3, 30) --> 30/03/2022
    datetime.datetime(2022, 3, 24, 15, 8, 5, 965163, tzinfo=datetime.timezone.utc) --> 24/03/2022
    None, '' --> ''
    """
    if date:
        return date.strftime(format)
    return ""


def phone_number_is_valid(phone_number):
    """
    Ways to check if a phone number is valid:
    - phonenumbers.is_valid_number(number_string) / returns True or False
    - PhoneNumber.from_string(number_string).is_valid() / returns True or NumberParseException.INVALID_COUNTRY_CODE  # noqa

    A number without a country code (example: +33) will be considered invalid.
    """
    try:
        return phonenumbers.is_valid_number(phonenumbers.parse(phone_number))
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
