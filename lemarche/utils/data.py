import io

import phonenumbers
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
    - with phonenumbers
        import phonenumbers
        phonenumbers.is_valid_number(number_string) / returns True or False
    - with PhoneNumber
        from phonenumber_field.phonenumber import PhoneNumber
        PhoneNumber.from_string(number_string).is_valid() / returns True or NumberParseException.INVALID_COUNTRY_CODE  # noqa

    A number without a country code (example: +33) will be considered invalid.
    """
    try:
        return phonenumbers.is_valid_number(phonenumbers.parse(phone_number))
    except phonenumbers.phonenumberutil.NumberParseException:
        return False


def phone_number_display(phone_number_model_field):
    """
    https://django-phonenumber-field.readthedocs.io/en/latest/reference.html
    phone.as_international --> +33 1 23 45 67 89
    phone.as_national --> 01 23 45 67 89
    phone.as_e164 --> +33123456789
    phone.as_rfc3966 --> tel:+33-1-23-45-67-89
    str(phone) --> +33123456789
    """
    try:
        return phone_number_model_field.as_e164
    except AttributeError:
        return phone_number_model_field
