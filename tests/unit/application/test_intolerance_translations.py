"""
Tests para translate_role() en app/adapters/intolerance_translations.py.

Cubre:
- Valores GL conocidos → traducción ES/EN
- Valor desconocido → fallback al original
- Fuera de contexto Flask → fallback al original (RuntimeError en get_locale)
"""

import pytest

from tests.conftest import TEST_CONFIG


@pytest.fixture(scope="module")
def flask_app():
    from app import create_app

    return create_app(test_config=TEST_CONFIG)


class TestTranslateRole:
    def test_coidadoras_to_spanish(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_role

        with flask_app.test_request_context():
            with force_locale("es"):
                assert translate_role("Coidadoras") == "Cuidadoras"

    def test_coidadoras_to_english(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_role

        with flask_app.test_request_context():
            with force_locale("en"):
                assert translate_role("Coidadoras") == "Carers"

    def test_coidadoras_galician_identity(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_role

        with flask_app.test_request_context():
            with force_locale("gl"):
                assert translate_role("Coidadoras") == "Coidadoras"

    def test_administrador_to_spanish(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_role

        with flask_app.test_request_context():
            with force_locale("es"):
                assert translate_role("Administrador") == "Administrador"

    def test_administrador_to_english(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_role

        with flask_app.test_request_context():
            with force_locale("en"):
                assert translate_role("Administrador") == "Administrator"

    def test_unknown_value_fallback(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_role

        with flask_app.test_request_context():
            with force_locale("es"):
                assert translate_role("UnknownRole") == "UnknownRole"

    def test_unknown_value_fallback_english(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_role

        with flask_app.test_request_context():
            with force_locale("en"):
                assert translate_role("NonExistent") == "NonExistent"

    def test_no_flask_context_returns_original(self):
        """Outside Flask context — get_locale raises RuntimeError → returns original."""
        from app.adapters.intolerance_translations import translate_role

        result = translate_role("Coidadoras")
        assert result == "Coidadoras"


class TestTranslateIntolerance:
    def test_glute_to_spanish(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_intolerance

        with flask_app.test_request_context():
            with force_locale("es"):
                assert translate_intolerance("Glute") == "Gluten"

    def test_glute_to_english(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_intolerance

        with flask_app.test_request_context():
            with force_locale("en"):
                assert translate_intolerance("Glute") == "Gluten"

    def test_unknown_intolerance_fallback(self, flask_app):
        from flask_babel import force_locale

        from app.adapters.intolerance_translations import translate_intolerance

        with flask_app.test_request_context():
            with force_locale("es"):
                assert translate_intolerance("SomethingNew") == "SomethingNew"

    def test_no_flask_context_returns_original(self):
        from app.adapters.intolerance_translations import translate_intolerance

        result = translate_intolerance("Glute")
        assert result == "Glute"
