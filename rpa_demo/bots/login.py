"""Flujo 1: formulario multipaso (login → verificar acceso → cerrar sesión)."""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from rpa_demo.exceptions import FormularioError
from rpa_demo.logger import log_step
from rpa_demo.selenium_helpers import (
    capturar_screenshot_en_error,
    escribir,
    esperar_elemento,
    esperar_y_click,
)

logger = logging.getLogger("rpa_demo")

URL = "https://the-internet.herokuapp.com/login"
MENSAJE_OK = "You logged into a secure area!"


def _rellenar_credenciales(driver: WebDriver, usuario: str, clave: str) -> None:
    """Escribe usuario y contraseña en el formulario."""
    escribir(driver, (By.ID, "username"), usuario)
    escribir(driver, (By.ID, "password"), clave)
    logger.info("✓ Credenciales introducidas")


def _verificar_acceso(driver: WebDriver) -> None:
    """Comprueba el aviso del sitio; si no es el de éxito, lanza FormularioError."""
    aviso = esperar_elemento(driver, (By.ID, "flash")).text
    if MENSAJE_OK not in aviso:
        raise FormularioError("LOGIN-RECHAZADO", f"El sitio respondió: {aviso.splitlines()[0]}")
    logger.info("✓ Acceso verificado")


@capturar_screenshot_en_error
def iniciar_sesion(driver: WebDriver, usuario: str, clave: str) -> None:
    """Inicia sesión, valida el resultado y cierra la sesión."""
    log_step(logger, 1, "Abriendo el formulario de login")
    driver.get(URL)

    log_step(logger, 2, "Rellenando credenciales")
    _rellenar_credenciales(driver, usuario, clave)

    log_step(logger, 3, "Enviando el formulario")
    esperar_y_click(driver, (By.CSS_SELECTOR, "button[type='submit']"))
    _verificar_acceso(driver)

    log_step(logger, 4, "Cerrando sesión")
    esperar_y_click(driver, (By.CSS_SELECTOR, "a.button.secondary"))
    esperar_elemento(driver, (By.ID, "username"))  # de vuelta al formulario
    logger.info("✓ Sesión cerrada")
