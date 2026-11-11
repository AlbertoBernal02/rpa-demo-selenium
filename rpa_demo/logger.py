"""Configuración de logs: consola + fichero `logs/<nombre>_<fecha>.log`."""

import logging
import sys
from datetime import datetime
from pathlib import Path

CARPETA_LOGS = Path("logs")


def configurar_logger(nombre: str = "rpa_demo") -> logging.Logger:
    """Devuelve un logger que escribe a consola y a un fichero con marca de tiempo."""
    logger = logging.getLogger(nombre)
    if logger.handlers:  # ya configurado (evita duplicar líneas si se llama dos veces)
        return logger

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows usa cp1252 por defecto
    logger.setLevel(logging.INFO)
    formato = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")

    CARPETA_LOGS.mkdir(exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    fichero = logging.FileHandler(CARPETA_LOGS / f"{nombre}_{marca}.log", encoding="utf-8")
    consola = logging.StreamHandler(sys.stdout)
    for handler in (fichero, consola):
        handler.setFormatter(formato)
        logger.addHandler(handler)
    return logger


def log_step(logger: logging.Logger, numero: int, texto: str) -> None:
    """Marca el inicio de un paso numerado del flujo."""
    logger.info(f"── Paso {numero}: {texto}")
