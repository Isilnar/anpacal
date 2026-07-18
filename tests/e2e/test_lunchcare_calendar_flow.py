"""
E2E tests: Lunchcare calendar flow (TC-LC-01 … TC-LC-05).

Cubre el flujo de calendario de comedor para usuarios con rol lunchcare:
  - Acceso no autenticado redirige a /login
  - Usuario lunchcare ve la página con #calendar (FullCalendar)
  - Botones de navegación de FullCalendar presentes
  - Click en día abre #selectLunchCareCalendarModal
  - El botón de cierre oculta el modal

Notas de diseño:
- cuidadora_seed es session-scoped: crea la escuela y el usuario de lunchcare
  UNA sola vez. Todos los tests de esta clase reutilizan esa sesión.
- La ruta GET /management_lunchcare_calendar renderiza lunchcare_calendar.html
  cuando el usuario tiene EXACTAMENTE 1 escuela en UserSchoolAssociation.
- El modal se abre mediante JavaScript (fetch + bootstrap.Modal.show).
  Se espera con wait_for_selector(state="visible") para garantizar que el
  fetch ha completado antes de hacer aserciones.
- Para disparar el click de día se usa select_event() via page.evaluate()
  para evitar problemas de headless con el handler dateClick de FullCalendar.
"""

import pytest


def _login(page, live_server_url, username, password):
    """Helper reutilizable: navega a /login y autentica al usuario."""
    page.goto(f"{live_server_url}/login")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    with page.expect_navigation(timeout=30000):
        page.locator('button[name="login-button"]').click()


@pytest.fixture
def lunchcare_page(page, live_server_url, cuidadora_seed):
    """Página ya autenticada como e2e_lunchcare_user y en el calendario."""
    creds = cuidadora_seed["lunchcare"]
    _login(page, live_server_url, creds["username"], creds["password"])
    page.goto(f"{live_server_url}/management_lunchcare_calendar")
    page.wait_for_load_state("load")
    return page


@pytest.mark.e2e
class TestLunchcareCalendarFlow:
    def test_tc_lc_01_unauthenticated_redirects_to_login(self, fresh_page, live_server_url):
        """TC-LC-01: Acceso sin autenticación redirige a /login."""
        fresh_page.goto(f"{live_server_url}/management_lunchcare_calendar")
        assert "/login" in fresh_page.url

    def test_tc_lc_02_lunchcare_user_sees_calendar(self, lunchcare_page):
        """TC-LC-02: Usuario lunchcare ve la página con el elemento #calendar."""
        # No debe haber redirigido a /login
        assert "/login" not in lunchcare_page.url
        # El div de FullCalendar debe estar en el DOM
        assert lunchcare_page.locator("#calendar").count() > 0

    def test_tc_lc_03_fullcalendar_nav_buttons_present(self, lunchcare_page):
        """TC-LC-03: Los botones de navegación de FullCalendar están presentes."""
        assert lunchcare_page.locator(".fc-prev-button").count() > 0, (
            "Botón 'Mes anterior' (.fc-prev-button) no encontrado"
        )
        assert lunchcare_page.locator(".fc-next-button").count() > 0, (
            "Botón 'Mes siguiente' (.fc-next-button) no encontrado"
        )
        assert lunchcare_page.locator(".fc-today-button").count() > 0, "Botón 'Hoy' (.fc-today-button) no encontrado"

    def test_tc_lc_04_day_click_opens_lunchcare_modal(self, lunchcare_page):
        """TC-LC-04: Click en un día del calendario abre #selectLunchCareCalendarModal.

        Estrategia:
        - Obtener via JS el primer .fc-daygrid-day que NO tenga fc-day-disabled.
        - Llamar directamente a select_event(dateStr) via page.evaluate() para
          disparar el handler sin depender del click en headless.
        """
        # Obtener el data-date del primer día clickeable visible
        date_str = lunchcare_page.evaluate("""
            () => {
                const cells = Array.from(
                    document.querySelectorAll('.fc-daygrid-day:not(.fc-day-disabled)')
                );
                const future = cells.find(c => {
                    const d = c.getAttribute('data-date');
                    return d && new Date(d) >= new Date();
                });
                const cell = future || cells[0];
                return cell ? cell.getAttribute('data-date') : null;
            }
        """)
        assert date_str is not None, "No se encontró ningún día clickeable en el calendario"

        # Disparar el handler JS directamente
        lunchcare_page.evaluate(f"select_event('{date_str}')")

        # Esperar a que el modal sea visible
        lunchcare_page.wait_for_selector("#selectLunchCareCalendarModal", state="visible", timeout=8000)

        # El título del modal (#calendarInterval) debe tener texto con la fecha
        interval_text = lunchcare_page.locator("#calendarInterval").inner_text()
        assert len(interval_text.strip()) > 0, "#calendarInterval está vacío tras abrir el modal"

    def test_tc_lc_05_modal_close_button_works(self, lunchcare_page):
        """TC-LC-05: El botón Cancelar cierra el modal #selectLunchCareCalendarModal.

        Abre el modal disparando select_event() y luego llama cancelEvents().
        Verifica que el modal deja de ser visible.
        """
        # Obtener cualquier día clickeable para abrir el modal
        date_str = lunchcare_page.evaluate("""
            () => {
                const cells = Array.from(
                    document.querySelectorAll('.fc-daygrid-day:not(.fc-day-disabled)')
                );
                const cell = cells[0];
                return cell ? cell.getAttribute('data-date') : null;
            }
        """)
        assert date_str is not None, "No hay días clickeables en el calendario"

        # Abrir el modal
        lunchcare_page.evaluate(f"select_event('{date_str}')")
        lunchcare_page.wait_for_selector("#selectLunchCareCalendarModal", state="visible", timeout=8000)

        # Llamar a cancelEvents() (botón Cancelar del modal)
        lunchcare_page.evaluate("cancelEvents()")

        # El modal debe cerrarse
        lunchcare_page.wait_for_selector("#selectLunchCareCalendarModal", state="hidden", timeout=5000)
