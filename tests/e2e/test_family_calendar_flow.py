"""
E2E tests: Family calendar flow (TC-FM-01 … TC-FM-06).

Cubre el flujo de calendario de familia para usuarios con rol family:
  - Acceso no autenticado redirige a /login
  - Usuario family ve la página con #calendar (FullCalendar)
  - Botones de navegación de FullCalendar presentes
  - Click en día (no bloqueado) abre #selectCalendarModal
  - El modal contiene #selectCalendarModalStudentsSection
  - El botón Cancelar cierra el modal

Notas de diseño:
- family_seed es session-scoped: crea la escuela, el alumno y el usuario family
  UNA sola vez. Todos los tests de esta clase reutilizan esa sesión.
- La ruta GET /management_calendar renderiza calendar.html cuando el usuario
  tiene EXACTAMENTE 1 escuela vinculada via alumnos (current_user.students).
- calendar.html pasa disabled_calendar_dates = get_dates_between(start, today)
  lo que bloquea todas las fechas anteriores al día actual. El test selecciona
  una fecha FUTURA usando JS para evitar que el load_event() la descarte.
- El modal #selectCalendarModal se abre con bootstrap.Modal.show() tras un
  fetch a /load_calendar_event. Se usa wait_for_selector(state="visible").
- Para disparar el click se usa load_event() via page.evaluate() para evitar
  problemas con el dateClick handler de FullCalendar en modo headless.
"""

from datetime import datetime, timedelta

import pytest


def _login(page, live_server_url, username, password):
    """Helper reutilizable: navega a /login y autentica al usuario."""
    page.goto(f"{live_server_url}/login")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    with page.expect_navigation(timeout=30000):
        page.locator('button[name="login-button"]').click()


def _next_weekday(days_ahead=1):
    """Devuelve la fecha de un día laborable próximo en formato YYYY-MM-DD."""
    candidate = datetime.now() + timedelta(days=days_ahead)
    # Saltar fines de semana (weekends=False en el calendario)
    while candidate.weekday() >= 5:  # 5=Sábado, 6=Domingo
        candidate += timedelta(days=1)
    return candidate.strftime("%Y-%m-%d")


@pytest.fixture
def family_page(page, live_server_url, family_seed):
    """Página ya autenticada como e2e_family_user y en el calendario de familia."""
    _login(page, live_server_url, family_seed["username"], family_seed["password"])
    page.goto(f"{live_server_url}/management_calendar")
    page.wait_for_load_state("load")
    return page


@pytest.mark.e2e
class TestFamilyCalendarFlow:
    def test_tc_fm_01_unauthenticated_redirects_to_login(self, fresh_page, live_server_url):
        """TC-FM-01: Acceso sin autenticación redirige a /login."""
        fresh_page.goto(f"{live_server_url}/management_calendar")
        assert "/login" in fresh_page.url

    def test_tc_fm_02_family_user_sees_calendar(self, family_page):
        """TC-FM-02: Usuario family ve la página con el elemento #calendar."""
        # No debe haber redirigido a /login
        assert "/login" not in family_page.url
        # El div de FullCalendar debe estar en el DOM
        assert family_page.locator("#calendar").count() > 0

    def test_tc_fm_03_fullcalendar_nav_buttons_present(self, family_page):
        """TC-FM-03: Los botones de navegación de FullCalendar están presentes."""
        assert family_page.locator(".fc-prev-button").count() > 0, (
            "Botón 'Mes anterior' (.fc-prev-button) no encontrado"
        )
        assert family_page.locator(".fc-next-button").count() > 0, (
            "Botón 'Mes siguiente' (.fc-next-button) no encontrado"
        )
        assert family_page.locator(".fc-today-button").count() > 0, "Botón 'Hoy' (.fc-today-button) no encontrado"

    def test_tc_fm_04_day_click_opens_family_modal(self, family_page):
        """TC-FM-04: Click en un día no bloqueado abre #selectCalendarModal.

        Estrategia:
        - Calcular una fecha laboral futura (Python) para garantizar que no
          está en disabled_calendar_dates (fechas pasadas) ni en disabled_dates
          (festivos: ninguno creado en este test suite).
        - Llamar load_event(dateStr) via page.evaluate() para disparar el
          handler JS que hace el fetch y abre el modal.
        """
        # Fecha laboral futura: no está en disabled_calendar_dates
        future_date = _next_weekday(days_ahead=1)

        # Navegar al mes de esa fecha si el calendario no la muestra
        family_page.evaluate(f"fullCalendar.gotoDate('{future_date}')")
        family_page.wait_for_load_state("load")

        # Disparar el handler JS load_event() (que hace el fetch + abre el modal)
        family_page.evaluate(f"load_event('{future_date}')")

        # Esperar a que el modal sea visible
        family_page.wait_for_selector("#selectCalendarModal", state="visible", timeout=8000)

        # El título del modal (#calendarInterval) debe tener texto con la fecha
        interval_text = family_page.locator("#calendarInterval").inner_html()
        assert len(interval_text.strip()) > 0, "#calendarInterval está vacío tras abrir el modal"

    def test_tc_fm_05_modal_has_students_section(self, family_page):
        """TC-FM-05: El modal tiene #selectCalendarModalStudentsSection.

        Verifica que la sección de alumnos del calendar_modal.html está en el DOM.
        Se abre el modal para confirmar que el elemento existe y es accesible.
        """
        # Abrir modal con fecha futura
        future_date = _next_weekday(days_ahead=2)
        family_page.evaluate(f"fullCalendar.gotoDate('{future_date}')")
        family_page.evaluate(f"load_event('{future_date}')")
        family_page.wait_for_selector("#selectCalendarModal", state="visible", timeout=8000)

        # La sección de alumnos debe existir en el DOM del modal
        assert family_page.locator("#selectCalendarModalStudentsSection").count() > 0, (
            "#selectCalendarModalStudentsSection no encontrado en el modal"
        )

    def test_tc_fm_06_cancel_button_closes_modal(self, family_page):
        """TC-FM-06: El botón Cancelar cierra el modal #selectCalendarModal.

        Abre el modal disparando load_event() y luego llama cancelEvents().
        Verifica que el modal deja de ser visible.
        """
        # Abrir modal con fecha futura
        future_date = _next_weekday(days_ahead=3)
        family_page.evaluate(f"fullCalendar.gotoDate('{future_date}')")
        family_page.evaluate(f"load_event('{future_date}')")
        family_page.wait_for_selector("#selectCalendarModal", state="visible", timeout=8000)

        # Llamar a cancelEvents() (botón Cancelar del modal)
        family_page.evaluate("cancelEvents()")

        # El modal debe cerrarse
        family_page.wait_for_selector("#selectCalendarModal", state="hidden", timeout=5000)
