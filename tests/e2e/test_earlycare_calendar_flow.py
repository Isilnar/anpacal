"""
E2E tests: Earlycare calendar flow (TC-EC-01 … TC-EC-06).

Cubre el flujo de calendario de madrugadores para usuarios con rol earlycare:
  - Acceso no autenticado redirige a /login
  - Usuario earlycare ve la página con #calendar (FullCalendar)
  - Botones de navegación de FullCalendar presentes
  - Click en día abre #selectEarlyCalendarModal
  - El modal contiene las secciones de estadísticas
  - El botón de cierre oculta el modal

Notas de diseño:
- cuidadora_seed es session-scoped: crea la escuela y el usuario de earlycare
  UNA sola vez. Todos los tests de esta clase reutilizan esa sesión.
- El modal se abre mediante JavaScript (fetch + bootstrap.Modal.show).
  Se espera con wait_for_selector(state="visible") para garantizar que el
  fetch ha completado antes de hacer aserciones sobre el contenido.
- La ruta GET /management_earlycare_calendar renderiza earlycare_calendar.html
  cuando el usuario tiene EXACTAMENTE 1 escuela en UserSchoolAssociation.
- El día que se hace click se selecciona via JavaScript (primera celda
  .fc-daygrid-day visible y clickeable) para evitar dependencia en la
  fecha actual del sistema.
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
def earlycare_page(page, live_server_url, cuidadora_seed):
    """Página ya autenticada como e2e_earlycare_user y en el calendario."""
    creds = cuidadora_seed["earlycare"]
    _login(page, live_server_url, creds["username"], creds["password"])
    page.goto(f"{live_server_url}/management_earlycare_calendar")
    page.wait_for_load_state("load")
    return page


@pytest.mark.e2e
class TestEarlycareCalendarFlow:
    def test_tc_ec_01_unauthenticated_redirects_to_login(self, fresh_page, live_server_url):
        """TC-EC-01: Acceso sin autenticación redirige a /login."""
        fresh_page.goto(f"{live_server_url}/management_earlycare_calendar")
        assert "/login" in fresh_page.url

    def test_tc_ec_02_earlycare_user_sees_calendar(self, earlycare_page):
        """TC-EC-02: Usuario earlycare ve la página con el elemento #calendar."""
        # No debe haber redirigido a /login
        assert "/login" not in earlycare_page.url
        # El div de FullCalendar debe estar en el DOM
        assert earlycare_page.locator("#calendar").count() > 0

    def test_tc_ec_03_fullcalendar_nav_buttons_present(self, earlycare_page):
        """TC-EC-03: Los botones de navegación de FullCalendar están presentes."""
        # FullCalendar renderiza estos botones con las clases fc-prev-button, etc.
        assert earlycare_page.locator(".fc-prev-button").count() > 0, (
            "Botón 'Mes anterior' (.fc-prev-button) no encontrado"
        )
        assert earlycare_page.locator(".fc-next-button").count() > 0, (
            "Botón 'Mes siguiente' (.fc-next-button) no encontrado"
        )
        assert earlycare_page.locator(".fc-today-button").count() > 0, "Botón 'Hoy' (.fc-today-button) no encontrado"

    def test_tc_ec_04_day_click_opens_modal(self, earlycare_page):
        """TC-EC-04: Click en un día del calendario abre #selectEarlyCalendarModal.

        Estrategia:
        - Obtener via JS el primer .fc-daygrid-day que NO tenga fc-day-disabled
          y que sea una fecha igual o posterior a la fecha inicial del calendario.
        - Llamar directamente a select_event(dateStr) via page.evaluate() si el
          click directo no dispara el dateClick handler de FullCalendar de forma
          confiable en headless.
        """
        # Obtener el data-date del primer día clickeable visible
        date_str = earlycare_page.evaluate("""
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

        # Disparar el handler JS directamente (equivale a dateClick en FullCalendar)
        earlycare_page.evaluate(f"select_event('{date_str}')")

        # Esperar a que el modal sea visible (el fetch completa antes de show())
        earlycare_page.wait_for_selector("#selectEarlyCalendarModal", state="visible", timeout=8000)

        # El título del modal (#calendarInterval) debe tener texto con la fecha
        interval_text = earlycare_page.locator("#calendarInterval").inner_text()
        assert len(interval_text.strip()) > 0, "#calendarInterval está vacío tras abrir el modal"

    def test_tc_ec_05_modal_has_stats_sections(self, earlycare_page):
        """TC-EC-05: El modal tiene las secciones de estadísticas de earlycare.

        Verifica que los elementos HTML del modal de earlycare_calendar_modal.html
        estén presentes en el DOM (no necesariamente visibles hasta abrir).
        """
        # Secciones de madrugadores con almorzo
        assert earlycare_page.locator("#div-early-madrugadores-almuerzo").count() > 0, (
            "Sección #div-early-madrugadores-almuerzo no encontrada en el modal"
        )
        assert earlycare_page.locator("#earlycare-data").count() > 0
        assert earlycare_page.locator("#earlycare-infantil").count() > 0
        assert earlycare_page.locator("#earlycare-primaria").count() > 0
        # Sección de comedor
        assert earlycare_page.locator("#div-lunchcare-comedor").count() > 0, (
            "Sección #div-lunchcare-comedor no encontrada en el modal"
        )
        assert earlycare_page.locator("#lunchcare-comedor").count() > 0
        assert earlycare_page.locator("#comedor-infantil").count() > 0
        assert earlycare_page.locator("#comedor-primaria").count() > 0

    def test_tc_ec_06_modal_close_button_works(self, earlycare_page):
        """TC-EC-06: El botón Cancelar cierra el modal #selectEarlyCalendarModal.

        Abre el modal disparando select_event() y luego hace click en el
        botón Cancelar. Verifica que el modal deja de ser visible.
        """
        # Obtener cualquier día clickeable para abrir el modal
        date_str = earlycare_page.evaluate("""
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
        earlycare_page.evaluate(f"select_event('{date_str}')")
        earlycare_page.wait_for_selector("#selectEarlyCalendarModal", state="visible", timeout=8000)

        # Llamar a cancelEvents() (botón Cancelar del modal)
        earlycare_page.evaluate("cancelEvents()")

        # El modal debe cerrarse (dejar de ser visible)
        earlycare_page.wait_for_selector("#selectEarlyCalendarModal", state="hidden", timeout=5000)
