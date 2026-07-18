"""
E2E tests: School management flow.

Cubre el CRUD completo de escuelas via la UI:
  - GET /management/schools/ carga correctamente
  - Crear una nueva escuela via formulario
  - Editar el nombre de una escuela existente
  - Borrar una escuela

Notas de diseño:
- admin_seed es session-scoped → nombres únicos con timestamp para evitar
  colisiones entre runs.
- Todas las acciones se hacen a través de la UI (no directamente en la DB)
  porque el server usa SQLite :memory:.
- Los botones "Gardar" y "Borrar" llaman JS que cambia el action del form
  antes de hacer submit → click directo sobre los elementos DOM.
- No se testea el flash message exacto (varía con i18n/galego). Se verifica
  que la acción tuvo efecto observando el DOM resultante.
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


def _unique_school_name():
    """Genera un nombre único para evitar colisiones con la DB :memory: session-scoped."""
    return f"E2E School {int(time.time() * 1000) % 100000}"


@pytest.mark.e2e
class TestSchoolFlow:
    def test_school_list_loads(self, admin_page, live_server_url):
        """GET /management/schools/ carga con status 200 y muestra el formulario."""
        admin_page.goto(f"{live_server_url}/management/schools/")
        admin_page.wait_for_load_state("load")

        # No redirige a login
        assert "/login" not in admin_page.url
        # El select de centros debe existir
        assert admin_page.locator("#selectedCenter").count() > 0
        # El input de nombre debe existir
        assert admin_page.locator("#centerName").count() > 0

    def test_create_school_flow(self, admin_page, live_server_url):
        """Rellenar el formulario de nueva escuela y guardar → aparece en el select."""
        school_name = _unique_school_name()

        admin_page.goto(f"{live_server_url}/management/schools/")
        admin_page.wait_for_load_state("load")

        # La opción "Novo centro" (value=0) ya debe estar seleccionada por defecto
        # Rellenar los campos del formulario
        admin_page.fill("#centerName", school_name)
        admin_page.fill("#centerPhone", "981000001")
        admin_page.fill("#centerMail", "e2e@test.com")
        admin_page.fill("#centerAddress", "Rúa E2E, 1")

        # Clic en "Gardar" → JS llama saveCenter() que hace submit con action POST /
        admin_page.click("button.btn-success")
        admin_page.wait_for_load_state("load")

        # Debe seguir en la misma página (redirect back a list)
        assert "/management/schools/" in admin_page.url

        # El nuevo nombre debe aparecer como opción en el select
        option = admin_page.locator(f'#selectedCenter option:text-is("{school_name}")')
        assert option.count() > 0, f"La escuela '{school_name}' no aparece en el select tras crear."

    def test_edit_school_flow(self, admin_page, live_server_url):
        """Seleccionar escuela existente → modificar nombre → guardar → nombre actualizado."""
        # Primero creamos una escuela para editar
        original_name = _unique_school_name()
        edited_name = original_name + " EDITED"

        admin_page.goto(f"{live_server_url}/management/schools/")
        admin_page.wait_for_load_state("load")

        # Crear la escuela base
        admin_page.fill("#centerName", original_name)
        admin_page.fill("#centerPhone", "981000002")
        admin_page.fill("#centerMail", "edit@test.com")
        admin_page.fill("#centerAddress", "Rúa Edit, 2")
        admin_page.click("button.btn-success")
        admin_page.wait_for_load_state("load")

        # Verificar que se creó
        option = admin_page.locator(f'#selectedCenter option:text-is("{original_name}")')
        assert option.count() > 0, "La escuela base no se creó correctamente."

        # Seleccionar la escuela creada en el select (dispara changeCenter + loadCenter)
        admin_page.select_option("#selectedCenter", label=original_name)
        # Esperar a que el fetch AJAX complete y rellene los inputs
        admin_page.wait_for_function(
            f'document.getElementById("centerName").value === "{original_name}"',
            timeout=5000,
        )

        # Modificar el nombre
        admin_page.fill("#centerName", edited_name)

        # Guardar (JS detecta centerId != 0 → POST /<id>)
        admin_page.click("button.btn-success")
        admin_page.wait_for_load_state("load")

        # El nombre editado debe aparecer en el select
        edited_option = admin_page.locator(f'#selectedCenter option:text-is("{edited_name}")')
        assert edited_option.count() > 0, f"El nombre editado '{edited_name}' no aparece en el select."

        # El nombre original no debe aparecer
        original_option = admin_page.locator(f'#selectedCenter option:text-is("{original_name}")')
        assert original_option.count() == 0, f"El nombre original '{original_name}' sigue en el select tras editar."

    def test_delete_school_flow(self, admin_page, live_server_url):
        """Seleccionar escuela → borrar → ya no aparece en el select."""
        school_name = _unique_school_name()

        admin_page.goto(f"{live_server_url}/management/schools/")
        admin_page.wait_for_load_state("load")

        # Crear la escuela que vamos a borrar
        admin_page.fill("#centerName", school_name)
        admin_page.fill("#centerPhone", "981000003")
        admin_page.fill("#centerMail", "delete@test.com")
        admin_page.fill("#centerAddress", "Rúa Delete, 3")
        admin_page.click("button.btn-success")
        admin_page.wait_for_load_state("load")

        # Verificar que se creó
        option = admin_page.locator(f'#selectedCenter option:text-is("{school_name}")')
        assert option.count() > 0, "La escuela a borrar no se creó correctamente."

        # Seleccionar la escuela (dispara changeCenter)
        admin_page.select_option("#selectedCenter", label=school_name)
        admin_page.wait_for_function(
            f'document.getElementById("centerName").value === "{school_name}"',
            timeout=5000,
        )

        # Esperar que el botón "Borrar" sea visible (JS lo muestra cuando centerId != 0)
        admin_page.wait_for_selector('#deleteCenterBtn:not([style*="display: none"])', timeout=3000)

        # Clic en "Borrar" → JS llama deleteCenter() → POST /<id>/delete
        admin_page.click("#deleteCenterBtn")
        admin_page.wait_for_load_state("load")

        # La escuela ya no debe aparecer en el select
        deleted_option = admin_page.locator(f'#selectedCenter option:text-is("{school_name}")')
        assert deleted_option.count() == 0, f"La escuela '{school_name}' sigue en el select tras borrar."
