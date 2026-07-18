"""
db_label_translations.py — Translation maps for DB-stored label values.

These strings live in the DB (Galician by default) and cannot be extracted by pybabel.
The adapter layer applies locale-aware translation at request time using these maps.

Keys   : exact description values stored in the DB (Galician).
Values : dict with 'es' and 'en' translations.  'gl' is the identity (DB value).

Usage::

    from app.adapters.intolerance_translations import translate_intolerance, translate_role
    label = translate_intolerance("Glute")      # → "Gluten" in ES/EN
    label = translate_role("Coidadoras")        # → "Cuidadoras" in ES, "Carers" in EN
"""

from __future__ import annotations

from flask_babel import get_locale

# ---------------------------------------------------------------------------
# Intolerance translation table — key = exact DB value (Galician)
# ---------------------------------------------------------------------------
_TRANSLATIONS: dict[str, dict[str, str]] = {
    "Cefal\u00f3podos": {
        "es": "Cef\u00e1lopodos",
        "en": "Cephalopods",
    },
    "Crust\u00e1ceos": {
        "es": "Crust\u00e1ceos",
        "en": "Crustaceans",
    },
    "E410 e E412": {
        "es": "E410 y E412",
        "en": "E410 and E412",
    },
    "Froita de \u00f3so": {
        "es": "Fruta de hueso",
        "en": "Stone fruit",
    },
    "Froitos Secos": {
        "es": "Frutos Secos",
        "en": "Tree Nuts",
    },
    "Fructosa": {
        "es": "Fructosa",
        "en": "Fructose",
    },
    "F\u00e1cil Masticaci\u00f3n": {
        "es": "F\u00e1cil Masticaci\u00f3n",
        "en": "Easy Chewing",
    },
    "Glute": {
        "es": "Gluten",
        "en": "Gluten",
    },
    "Legumes": {
        "es": "Legumbres",
        "en": "Legumes",
    },
    "L\u00e1cteos": {
        "es": "L\u00e1cteos",
        "en": "Dairy",
    },
    "Moluscos": {
        "es": "Moluscos",
        "en": "Molluscs",
    },
    "Ovos": {
        "es": "Huevos",
        "en": "Eggs",
    },
    "Peixe": {
        "es": "Pescado",
        "en": "Fish",
    },
    "Soia": {
        "es": "Soja",
        "en": "Soy",
    },
}


# ---------------------------------------------------------------------------
# Role translation table — key = exact DB value (Galician)
# ---------------------------------------------------------------------------
_ROLE_TRANSLATIONS: dict[str, dict[str, str]] = {
    "Administrador": {
        "es": "Administrador",
        "en": "Administrator",
    },
    "Familia": {
        "es": "Familia",
        "en": "Family",
    },
    "Coidadoras": {
        "es": "Cuidadoras",
        "en": "Carers",
    },
    "Catering": {
        "es": "Catering",
        "en": "Catering",
    },
}


def _translate(description: str, table: dict[str, dict[str, str]]) -> str:
    """Shared locale-aware lookup. Falls back to the original value on any miss."""
    try:
        locale = str(get_locale())
    except RuntimeError:
        return description

    lang = locale.split("_")[0]  # 'es_ES' → 'es'
    if lang == "gl":
        return description

    entry = table.get(description)
    if entry is None:
        return description

    return entry.get(lang, description)


def translate_intolerance(description: str) -> str:
    """Return the locale-aware label for a DB intolerance description."""
    return _translate(description, _TRANSLATIONS)


def translate_intolerance_in_text(text: str) -> str:
    """Translate all known DB intolerance names within a formatted text string.

    Looks up each intolerance description (case-insensitive) in the translation
    table and replaces it with the locale-aware label.  Unknown tokens are left
    as-is.  Use this when the intolerance descriptions are already embedded in
    a larger string (e.g. ``"1 alerxia/s glute"``) and you want to translate
    just the intolerance names.
    """
    if not text:
        return text
    result = text
    for db_name in _TRANSLATIONS:
        translated = _translate(db_name, _TRANSLATIONS)
        if translated.lower() != db_name.lower():
            # Replace preserving the lowercase form used in the assembled string
            result = result.replace(db_name.lower(), translated.lower())
    return result


def translate_role(description: str) -> str:
    """Return the locale-aware label for a DB role description."""
    return _translate(description, _ROLE_TRANSLATIONS)
