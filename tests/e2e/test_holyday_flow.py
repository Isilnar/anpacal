"""
E2E tests: Holyday (festivos) management flow.

Cubre el CRUD de festivos via la UI:
  - GET /management/holydays/ carga correctamente
  - Crear un nuevo festivo via formulario
  - Borrar un festivo existente

Notas de diseño:
- El campo de fecha es un `<input type="text" id="dataHolydayDateValue" readonly>`
  manejado por flatpickr. Playwright no puede hacer fill() en inputs readonly,
  por lo que se usa page.evaluate() para asignar el valor directamente.
- El formato de fecha esperado por el backend es dd/mm/yyyy (strptime "%d/%m/%Y").
- No existe flujo de edit desde la UI actual de holydays (el botón "Borrar" solo
  aparece cuando se selecciona un festivo existente — no hay formulario de edición
  separado). Por eso solo se testean: list, create y delete.
- Los festivos usan una fecha única por test (año 2099, día variable por timestamp)
  para evitar DuplicateHolydayError con la DB :memory: session-scoped.
- CSS `option[value!="0"]` no es CSS estándar (negation de atributo) → se cuenta
  con page.evaluate() usando Array.filter() en JS.
"""

import time

import pytest


@pytest.fixture
def admin_page(page, live_server_url, admin_seed):
    """Página ya autenticada como e2e_admin."""
    page.goto(f"{live_server_url}/login")
    page.fill('input[name="username"]', admin_seed["username"])
    page.fill('input[name="password"]', admin_seed["password"])
    with page.expect_navigation(timeout=30000):
        page.locator('button[name="login-button"]').click()
    return page


def _unique_holyday_date():
    """Genera una fecha única para evitar DuplicateHolydayError.

    Usa los últimos dígitos del timestamp (módulo 28) para variar el día.
    Siempre en formato dd/mm/yyyy que espera el backend.
    """
    # Día del mes entre 1 y 28 basado en el timestamp → evita colisiones entre runs
    day = (int(time.time()) % 28) + 1
    # Año 2099 para no interferir con fechas reales de producción
    return f"{day:02d}/11/2099"


def _set_holyday_date(page, date_str):
    """Asigna la fecha en el input readonly de flatpickr via JavaScript."""
    page.evaluate(f'document.getElementById("dataHolydayDateValue").value = "{date_str}"')


def _count_real_holyday_options(page):
    """Cuenta las opciones del select excluyendo 'Novo festivo' (value=0).

    CSS `option[value!="0"]` no es CSS estándar — se evalúa con JS.
    """
    return page.evaluate(
        "Array.from(document.querySelectorAll('#selectedHolyday option')).filter(o => o.value !== '0').length"
    )


@pytest.mark.e2e
class TestHolydayFlow:
    def test_holyday_list_loads(self, admin_page, live_server_url):
        """GET /management/holydays/ carga correctamente y muestra el formulario."""
        admin_page.goto(f"{live_server_url}/management/holydays/")
        admin_page.wait_for_load_state("load")

        # No redirige a login
        assert "/login" not in admin_page.url
        # El select de festivos debe existir
        assert admin_page.locator("#selectedHolyday").count() > 0
        # El input de fecha debe existir
        assert admin_page.locator("#dataHolydayDateValue").count() > 0

    def test_create_holyday_flow(self, admin_page, live_server_url):
        """Rellenar el formulario de nuevo festivo y guardar → aparece en el select."""
        holyday_date = _unique_holyday_date()

        admin_page.goto(f"{live_server_url}/management/holydays/")
        admin_page.wait_for_load_state("load")

        # Contar opciones reales antes de crear
        options_before = _count_real_holyday_options(admin_page)

        # El input tiene readonly (puesto por flatpickr) → asignar valor via evaluate()
        _set_holyday_date(admin_page, holyday_date)

        # Verificar que el valor se asignó correctamente antes de hacer submit
        assert admin_page.locator("#dataHolydayDateValue").input_value() == holyday_date

        # Clic en "Gardar" → JS llama saveHolyday() → submit con action POST /
        admin_page.click("button.btn-success")
        admin_page.wait_for_load_state("load")

        # Debe permanecer en la misma página (redirect back a list)
        assert "/management/holydays/" in admin_page.url

        # Debe haber al menos una opción más que antes
        options_after = _count_real_holyday_options(admin_page)
        assert options_after > options_before, (
            f"El festivo para '{holyday_date}' no se creó (opciones antes: {options_before}, después: {options_after})."
        )

    def test_delete_holyday_flow(self, admin_page, live_server_url):
        """Seleccionar festivo existente → borrar → ya no aparece en el select."""
        holyday_date = _unique_holyday_date()

        admin_page.goto(f"{live_server_url}/management/holydays/")
        admin_page.wait_for_load_state("load")

        # Crear el festivo que vamos a borrar
        _set_holyday_date(admin_page, holyday_date)
        admin_page.click("button.btn-success")
        admin_page.wait_for_load_state("load")

        # Verificar que se creó
        options_after_create = _count_real_holyday_options(admin_page)
        assert options_after_create > 0, f"No hay festivos reales en el select tras crear '{holyday_date}'."

        # Obtener el value del último festivo creado (el último option con value != 0)
        option_value = admin_page.evaluate(
            "Array.from(document.querySelectorAll('#selectedHolyday option'))"
            ".filter(o => o.value !== '0').at(-1)?.value"
        )
        assert option_value is not None, "No se encontró ningún festivo real en el select."

        # Seleccionar el festivo (dispara changeHolyday → muestra deleteHolydayBtn)
        admin_page.select_option("#selectedHolyday", value=option_value)
        # Esperar a que JS muestre el botón "Borrar"
        admin_page.wait_for_selector('#deleteHolydayBtn:not([style*="display: none"])', timeout=3000)

        # Clic en "Borrar" → JS llama deleteHolyday() → POST /<id>/delete
        admin_page.click("#deleteHolydayBtn")
        admin_page.wait_for_load_state("load")

        # El número de opciones debe haber disminuido
        options_after_delete = _count_real_holyday_options(admin_page)
        assert options_after_delete < options_after_create, (
            f"El festivo no se borró del select "
            f"(opciones: antes de borrar={options_after_create}, después={options_after_delete})."
        )
