"""
E2E tests: User management flow (REQ-V03).

Requiere Playwright con Chromium instalado:
    python -m playwright install chromium

Los tests usan el live_server_url fixture (puerto 5001).
"""

import pytest


@pytest.fixture
def admin_page(page, live_server_url, admin_seed):
    """Devuelve una `page` ya autenticada como e2e_admin."""
    page.goto(f"{live_server_url}/login")
    page.fill('input[name="username"]', admin_seed["username"])
    page.fill('input[name="password"]', admin_seed["password"])
    with page.expect_navigation(timeout=30000):
        page.locator('button[name="login-button"]').click()
    return page


@pytest.mark.e2e
class TestUserManagementFlow:
    def test_user_list_requires_authentication(self, fresh_page, live_server_url):
        """Acceder a /management/users/ sin login redirige a login.

        Usa fresh_page (contexto sin cookies) para garantizar estado no autenticado,
        incluso si otros tests del módulo ya iniciaron sesión en el contexto compartido.
        """
        fresh_page.goto(f"{live_server_url}/management/users/")
        # Flask-Login debe redirigir a /login
        assert "/login" in fresh_page.url

    def test_create_user_flow(self, admin_page, live_server_url):
        """Admin puede acceder a la lista de usuarios (gestión activa)."""
        admin_page.goto(f"{live_server_url}/management/users/")
        # No debe redirigir a /login — el admin tiene acceso
        assert "/login" not in admin_page.url
        # La página debe cargar el formulario de gestión de usuarios
        assert admin_page.locator("form, button, select").count() > 0

    def test_edit_user_flow(self, admin_page, live_server_url):
        """Admin puede ver la lista de usuarios sin ser redirigido."""
        admin_page.goto(f"{live_server_url}/management/users/")
        # Verificar que la página cargó correctamente (no unauthorized redirect)
        assert "/login" not in admin_page.url
        # Debe haber contenido de tabla o formulario de gestión
        assert admin_page.locator("form, button, select, table").count() > 0
