"""Flujo 2: contenido que aparece de forma asíncrona (sin `time.sleep`, solo esperas explícitas)."""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from rpa_demo.logger import log_step
from rpa_demo.selenium_helpers import (
    capturar_screenshot_en_error,
    esperar_elemento,
    esperar_y_click,
)

logger = logging.getLogger("rpa_demo")

URL = "https://the-internet.herokuapp.com/dynamic_loading/2"


@capturar_screenshot_en_error
def leer_contenido_dinamico(driver: WebDriver) -> str:
    """Lanza la carga, espera a que el texto exista en el DOM y lo devuelve."""
    log_step(logger, 1, "Abriendo la página")
    driver.get(URL)

    log_step(logger, 2, "Lanzando la carga asíncrona")
    esperar_y_click(driver, (By.CSS_SELECTOR, "#start button"))

    log_step(logger, 3, "Esperando al contenido")
    texto = esperar_elemento(driver, (By.CSS_SELECTOR, "#finish h4"), timeout=15).text
    logger.info(f"✓ Contenido recibido: {texto!r}")
    return texto
