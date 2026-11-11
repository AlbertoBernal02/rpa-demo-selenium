"""Flujo 3: descarga de un documento y comprobación de que llegó completo."""

import logging
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from rpa_demo.exceptions import DescargaError
from rpa_demo.logger import log_step
from rpa_demo.selenium_helpers import (
    capturar_screenshot_en_error,
    esperar_descarga,
    esperar_elemento,
    esperar_y_click,
    vaciar_carpeta,
)

logger = logging.getLogger("rpa_demo")

URL = "https://the-internet.herokuapp.com/download"


@capturar_screenshot_en_error
def descargar_primer_documento(driver: WebDriver, carpeta: Path) -> Path:
    """Descarga el primer enlace de la lista y valida que el fichero no esté vacío."""
    log_step(logger, 1, "Abriendo la lista de documentos")
    vaciar_carpeta(carpeta)
    driver.get(URL)
    enlace = (By.CSS_SELECTOR, ".example a")
    nombre = esperar_elemento(driver, enlace).text
    logger.info(f"Documento elegido: {nombre}")

    log_step(logger, 2, "Lanzando la descarga")
    esperar_y_click(driver, enlace)

    log_step(logger, 3, "Esperando al fichero")
    ruta = esperar_descarga(carpeta)
    if ruta.stat().st_size == 0:
        raise DescargaError("VACIO", f"{ruta.name} se descargó con 0 bytes")
    logger.info(f"✓ Descargado {ruta.name} ({ruta.stat().st_size} bytes)")
    return ruta
