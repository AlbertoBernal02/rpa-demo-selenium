"""Pruebas de las utilidades que no necesitan navegador."""

import threading
import time

import pytest

from rpa_demo.exceptions import DescargaError, FormularioError
from rpa_demo.selenium_helpers import esperar_descarga


def test_el_codigo_de_error_lleva_prefijo_y_detalle():
    error = FormularioError("LOGIN-RECHAZADO", "contraseña incorrecta")
    assert error.codigo == "FORM-LOGIN-RECHAZADO"
    assert "contraseña incorrecta" in str(error)


def test_esperar_descarga_devuelve_el_fichero_cuando_termina(tmp_path):
    def _simular_descarga():
        time.sleep(0.5)
        (tmp_path / "doc.crdownload").write_text("parcial")
        time.sleep(0.5)
        (tmp_path / "doc.crdownload").rename(tmp_path / "doc.txt")

    threading.Thread(target=_simular_descarga).start()
    assert esperar_descarga(tmp_path, timeout=5).name == "doc.txt"


def test_esperar_descarga_ignora_el_nombre_temporal_de_chrome(tmp_path):
    (tmp_path / "abc123.tmp").write_text("parcial")
    with pytest.raises(DescargaError):  # solo hay un temporal: la descarga no ha terminado
        esperar_descarga(tmp_path, timeout=1)


def test_esperar_descarga_lanza_error_si_no_llega_nada(tmp_path):
    with pytest.raises(DescargaError) as e:
        esperar_descarga(tmp_path, timeout=1)
    assert e.value.codigo == "DESC-NO-LLEGA"
