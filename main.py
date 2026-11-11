"""Orquestador: ejecuta los bots, cronometra cada uno y escribe `resultado.json`.

Uso:
    python main.py                  # los tres flujos, sin ventana
    python main.py --visible        # con el navegador a la vista
    python main.py --simular-fallo  # contraseña errónea: muestra el log y la captura de error
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from rpa_demo.bots.descarga import descargar_primer_documento
from rpa_demo.bots.espera_dinamica import leer_contenido_dinamico
from rpa_demo.bots.login import iniciar_sesion
from rpa_demo.exceptions import RPAError
from rpa_demo.logger import configurar_logger
from rpa_demo.selenium_helpers import crear_driver

CARPETA_DESCARGAS = Path("descargas")
FICHERO_RESULTADO = Path("resultado.json")

# Credenciales públicas del sitio de pruebas (están en su propia página de login).
USUARIO = "tomsmith"
CLAVE = "SuperSecretPassword!"


def ejecutar_bot(nombre: str, accion) -> dict:
    """Ejecuta `accion()`, mide el tiempo y devuelve un resumen con estado y código de error."""
    logger = logging.getLogger("rpa_demo")
    logger.info(f"▶ Bot «{nombre}»")
    inicio = time.monotonic()
    resumen = {"bot": nombre, "estado": "OK", "codigo_error": None, "detalle": None}
    try:
        resultado = accion()
        resumen["detalle"] = str(resultado) if resultado is not None else None
    except RPAError as e:
        resumen.update(estado="ERROR", codigo_error=e.codigo, detalle=e.mensaje)
    except Exception as e:  # cualquier otro fallo se informa igual, sin tumbar el resto
        resumen.update(estado="ERROR", codigo_error="INESPERADO", detalle=str(e))
    resumen["segundos"] = round(time.monotonic() - inicio, 1)
    simbolo = "✓" if resumen["estado"] == "OK" else "✗"
    logger.info(f"{simbolo} Bot «{nombre}» → {resumen['estado']} en {resumen['segundos']} s")
    return resumen


def main() -> int:
    parser = argparse.ArgumentParser(description="Demo de bots con Python y Selenium")
    parser.add_argument("--visible", action="store_true", help="mostrar el navegador")
    parser.add_argument("--simular-fallo", action="store_true", help="usar una contraseña incorrecta")
    args = parser.parse_args()

    logger = configurar_logger()
    driver = crear_driver(CARPETA_DESCARGAS, headless=not args.visible)
    clave = "incorrecta" if args.simular_fallo else CLAVE

    try:
        resultados = [
            ejecutar_bot("login", lambda: iniciar_sesion(driver, USUARIO, clave)),
            ejecutar_bot("espera_dinamica", lambda: leer_contenido_dinamico(driver)),
            ejecutar_bot("descarga", lambda: descargar_primer_documento(driver, CARPETA_DESCARGAS)),
        ]
    finally:
        driver.quit()

    FICHERO_RESULTADO.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    fallidos = [r for r in resultados if r["estado"] != "OK"]
    logger.info(f"Resumen: {len(resultados) - len(fallidos)}/{len(resultados)} bots correctos → {FICHERO_RESULTADO}")
    return 1 if fallidos else 0


if __name__ == "__main__":
    sys.exit(main())
