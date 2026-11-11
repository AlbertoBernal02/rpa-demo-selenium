"""Utilidades compartidas por todos los bots: driver, esperas, clicks y captura de errores."""

import functools
import logging
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from rpa_demo.exceptions import DescargaError, NavegacionError, RPAError

logger = logging.getLogger("rpa_demo")

CARPETA_CAPTURAS = Path("capturas")
TIMEOUT_POR_DEFECTO = 10
SUFIJOS_TEMPORALES = {".crdownload", ".tmp"}  # nombres que Chrome usa mientras descarga


def vaciar_carpeta(carpeta: Path) -> None:
    """Borra los ficheros previos para no confundirlos con la descarga nueva."""
    for fichero in carpeta.iterdir():
        if fichero.is_file():
            fichero.unlink()


def crear_driver(carpeta_descargas: Path, headless: bool = True) -> WebDriver:
    """Crea un Chrome configurado para descargar en `carpeta_descargas` sin diálogos."""
    carpeta_descargas.mkdir(parents=True, exist_ok=True)
    opciones = Options()
    if headless:
        opciones.add_argument("--headless=new")
    opciones.add_argument("--window-size=1280,900")
    opciones.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(carpeta_descargas.resolve()),
            "download.prompt_for_download": False,
        },
    )
    logger.info(f"Iniciando Chrome (headless={headless})")
    return webdriver.Chrome(options=opciones)  # Selenium Manager resuelve el chromedriver


def esperar_elemento(driver: WebDriver, localizador: tuple, timeout: int = TIMEOUT_POR_DEFECTO):
    """Espera a que el elemento sea visible; si no, lanza NavegacionError."""
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(localizador))
    except TimeoutException as e:
        raise NavegacionError("ELEMENTO-NO-APARECE", f"No apareció {localizador}") from e


def esperar_y_click(driver: WebDriver, localizador: tuple, timeout: int = TIMEOUT_POR_DEFECTO) -> None:
    """Espera a que sea clicable, centra el elemento y hace click con JS (evita overlays)."""
    try:
        elemento = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(localizador))
    except TimeoutException as e:
        raise NavegacionError("CLICK-NO-DISPONIBLE", f"No era clicable {localizador}") from e
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
    driver.execute_script("arguments[0].click();", elemento)


def escribir(driver: WebDriver, localizador: tuple, texto: str) -> None:
    """Rellena un campo de texto tras esperar a que sea visible."""
    campo = esperar_elemento(driver, localizador)
    campo.clear()
    campo.send_keys(texto)


def esperar_descarga(carpeta: Path, timeout: int = 15) -> Path:
    """Espera a que aparezca un fichero completo (sin `.crdownload`) y devuelve su ruta."""

    def _fichero_listo(_):
        ficheros = [f for f in carpeta.iterdir() if f.is_file()]
        if any(f.suffix in SUFIJOS_TEMPORALES for f in ficheros):
            return False  # Chrome sigue escribiendo
        return ficheros[0] if ficheros else False

    try:
        return WebDriverWait(None, timeout, poll_frequency=0.3).until(_fichero_listo)
    except TimeoutException as e:
        raise DescargaError("NO-LLEGA", f"No apareció ningún fichero en {carpeta}") from e


def capturar_screenshot_en_error(funcion):
    """Decorador: si el bot falla guarda una captura y deja el detalle en el log.

    El primer argumento de la función decorada debe ser el driver.
    """

    @functools.wraps(funcion)
    def envoltorio(driver: WebDriver, *args, **kwargs):
        try:
            return funcion(driver, *args, **kwargs)
        except Exception as e:
            codigo = e.codigo if isinstance(e, RPAError) else "INESPERADO"
            CARPETA_CAPTURAS.mkdir(exist_ok=True)
            marca = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta = CARPETA_CAPTURAS / f"error_{funcion.__name__}_{codigo}_{marca}.png"
            driver.save_screenshot(str(ruta))
            logger.error(f"✗ {funcion.__name__} falló ({codigo}): {e}")
            logger.error(f"  URL: {driver.current_url} · captura: {ruta}")
            raise

    return envoltorio
