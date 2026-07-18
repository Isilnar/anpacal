"""
E2E tests: Login flow (REQ-V03).

Requiere Playwright con Chromium instalado:
    python -m playwright install chromium

Los tests usan el live_server_url fixture (puerto 5001).
"""

import pytest


@pytest.mark.e2e
class TestLoginFlow:
    def test_login_page_loads(self, page, live_server_url):
        """La página de login debe mostrar el formulario."""
        page.goto(f"{live_server_url}/login")
        assert page.title() != ""
        # Verificar que existen los inputs de credenciales
        assert page.locator('input[name="username"]').count() > 0
        assert page.locator('input[name="password"]').count() > 0

    def test_login_with_invalid_credentials_shows_error(self, page, live_server_url):
        """Login con credenciales inválidas muestra error o vuelve a /login."""
        page.goto(f"{live_server_url}/login")
        page.fill('input[name="username"]', "invalid_user_xyz")
        page.fill('input[name="password"]', "wrong_password_xyz")
        page.locator('button[name="login-button"]').click()
        # Debe seguir en /login (redirect back) o mostrar mensaje de error
        assert "/login" in page.url or page.locator(".alert, .flash, .error").count() > 0

    def test_login_with_valid_credentials_redirects(self, page, live_server_url, admin_seed):
        """Login con credenciales válidas redirige fuera de /login."""
        page.goto(f"{live_server_url}/login")
        page.fill('input[name="username"]', admin_seed["username"])
        page.fill('input[name="password"]', admin_seed["password"])
        with page.expect_navigation(timeout=30000):
            page.locator('button[name="login-button"]').click()
        assert "/login" not in page.url
