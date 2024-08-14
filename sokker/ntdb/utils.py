from django.db.models import F, ExpressionWrapper, FloatField, CharField, Value

from django.db.models.functions import Concat


def get_fullname_wrapper():
    return ExpressionWrapper(
        Concat(F("name"), Value(" "), F("surname")),
        output_field=CharField(),
    )


def get_gk_wrapper():
    return ExpressionWrapper(
        2 * F("skillkeeper") + 1.5 * F("skillpace") + F("skillpassing"),
        output_field=FloatField(),
    )


def get_def_wrapper():
    return ExpressionWrapper(
        1.5 * F("skillpace")
        + 1.5 * F("skilldefending")
        + F("skillplaymaking")
        + F("skilltechnique")
        + 0.5 * F("skillpassing"),
        output_field=FloatField(),
    )


def get_mid_wrapper():
    return ExpressionWrapper(
        1.5 * F("skillpassing")
        + 1.5 * F("skillplaymaking")
        + F("skillpace")
        + F("skilltechnique")
        + F("skilldefending")
        + 0.5 * F("skillscoring")
        + 0.25 * F("skillstamina"),
        output_field=FloatField(),
    )


def get_att_wrapper():
    return ExpressionWrapper(
        F("skilltechnique") + F("skillpace") + F("skillscoring"),
        output_field=FloatField(),
    )
